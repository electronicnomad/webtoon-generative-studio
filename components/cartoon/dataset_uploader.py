import mesop as me
from dataclasses import dataclass, field, asdict
from typing import Callable, Optional, List, Dict
import datetime

from common.storage import store_to_gcs
from common.metadata import add_media_item, save_dataset, get_all_datasets, get_media_by_dataset, MediaItem
from common.utils import create_display_url
from state.state import AppState

@me.stateclass
class DatasetUploaderState:
    dataset_name: str = ""
    description: str = ""
    is_uploading: bool = False
    upload_status: str = ""
    active_uploads: int = 0 # Track concurrent uploads
    
    # New fields for enhancements
    is_new_dataset: bool = False
    selected_existing_dataset: str = ""
    existing_datasets: list[dict] = field(default_factory=list)
    
    # Thumbnail display
    dataset_assets: list[dict] = field(default_factory=list)
    asset_count: int = 0

@me.component
def dataset_uploader():
    """
    Component to upload assets to a specific dataset.
    """
    state = me.state(DatasetUploaderState)
    app_state = me.state(AppState)

    with me.box(style=me.Style(display="flex", flex_direction="column", gap=16, border=me.Border.all(me.BorderSide(width=1, color="#e0e0e0")), padding=me.Padding.all(16), border_radius=8)):
        me.text("Add to Dataset", type="headline-6")
        
        # Mode Toggle
        with me.box(style=me.Style(display="flex", flex_direction="row", gap=16, margin=me.Margin(bottom=16))):
            me.radio(
                options=[
                    me.RadioOption(label="Existing Project", value="existing"),
                    me.RadioOption(label="New Project", value="new"),
                ],
                on_change=on_mode_change,
                value="new" if state.is_new_dataset else "existing"
            )

        if state.is_new_dataset:
            # New Dataset Form
            me.input(
                label="Dataset Name (e.g. 'Project Alpha')",
                value=state.dataset_name,
                on_blur=on_dataset_name_input,
                key="dataset_name",
                style=me.Style(width="100%")
            )
            
            me.textarea(
                label="Description (Optional context for this dataset)",
                value=state.description,
                on_blur=on_description_input,
                key="dataset_description",
                style=me.Style(width="100%")
            )
        else:
            # Existing Dataset Selector
            if not state.existing_datasets:
                 me.text("No datasets found or not loaded. Click refresh.", style=me.Style(color="gray", font_size=12))
            
            with me.box(style=me.Style(display="flex", align_items="center", gap=8)):
                 options = [
                     me.SelectOption(label=d["name"], value=d["name"]) 
                     for d in state.existing_datasets
                 ]
                 me.select(
                     label="Select Existing Link/Project",
                     options=options,
                     value=state.selected_existing_dataset,
                     on_selection_change=on_existing_dataset_change,
                     style=me.Style(flex_grow=1),
                     key="existing_dataset_select"
                 )
                 with me.content_button(type="icon", on_click=on_refresh_datasets):
                     me.tooltip(message="Refresh Projects")
                     me.icon("refresh")

        me.uploader(
            label="Upload Assets (Images)",
            accepted_file_types=["image/jpeg", "image/png", "image/webp"],
            on_upload=on_file_upload,
            style=me.Style(width="100%"),
            multiple=True
        )
        me.text("Note: You can select multiple files if your browser calls for it, they will replace one by one if not handled carefully.", type="body-2", style=me.Style(color="gray"))

        if state.is_uploading:
            me.progress_spinner()
        
        if state.upload_status:
            me.text(state.upload_status)
            
        # Thumbnails Grid
        if state.asset_count > 0:
            me.divider()
            with me.box(style=me.Style(display="flex", align_items="center", gap=8)):
                me.text(f"Dataset Contents ({state.asset_count} assets)", type="subtitle-1", style=me.Style(font_weight="bold"))
                with me.content_button(type="icon", on_click=on_refresh_assets):
                    me.tooltip(message="Refresh Assets List")
                    me.icon("refresh")
            with me.box(style=me.Style(display="flex", flex_wrap="wrap", gap=8, max_height=300, overflow_y="auto")):
                for index, asset in enumerate(state.dataset_assets):
                    # Determine source URL
                    src = ""
                    if asset.get("thumbnail_uri"):
                         src = asset.get("thumbnail_uri")
                    elif asset.get("gcsuri"):
                         src = create_display_url(asset.get("gcsuri"))
                    elif asset.get("gcs_uris") and len(asset.get("gcs_uris")) > 0:
                         src = create_display_url(asset.get("gcs_uris")[0])
                    
                    if src:
                        # Use ID if available, otherwise index as fallback, but ID is better for updates
                        # If multiple assets have same ID (shouldn't happen), index might be safer?
                        # But we want to re-render new items at top. 
                        # Let's use ID if present.
                        asset_id = asset.get("id", f"temp_{index}")
                        me.image(
                            key=f"asset_{asset_id}",
                            src=src,
                            style=me.Style(width=80, height=80, object_fit="cover", border_radius=4, border=me.Border.all(me.BorderSide(width=1, color="#eee")))
                        )
        elif not state.is_new_dataset and state.selected_existing_dataset:
             me.text("No assets found in this dataset.", style=me.Style(color="gray", font_size=12))


def on_mode_change(e: me.RadioChangeEvent):
    state = me.state(DatasetUploaderState)
    state.is_new_dataset = (e.value == "new")
    if not state.is_new_dataset and not state.existing_datasets:
        # Auto-load
        load_datasets(state)

def on_refresh_datasets(e: me.ClickEvent):
    state = me.state(DatasetUploaderState)
    load_datasets(state)

def on_refresh_assets(e: me.ClickEvent):
    state = me.state(DatasetUploaderState)
    target_name = state.dataset_name if state.is_new_dataset else state.selected_existing_dataset
    if target_name:
        load_dataset_assets(state, target_name)

# Module-level cache to handle concurrency race conditions
# Key: dataset_name, Value: List[dict]
# This works because the Python process is shared (for this deployment) and GIL protects list appends.
_upload_cache: Dict[str, List[dict]] = {}

def get_cached_uploads(dataset_name: str) -> List[dict]:
    return _upload_cache.get(dataset_name, [])

def add_to_cache(dataset_name: str, item: dict):
    if dataset_name not in _upload_cache:
        _upload_cache[dataset_name] = []
    _upload_cache[dataset_name].insert(0, item)

def clear_cache(dataset_name: str):
    if dataset_name in _upload_cache:
        _upload_cache[dataset_name] = []

def load_datasets(state: DatasetUploaderState):
    raw_datasets = get_all_datasets()
    for d in raw_datasets:
        for k, v in d.items():
            if hasattr(v, 'isoformat'):
                d[k] = v.isoformat()
    state.existing_datasets = raw_datasets

def load_dataset_assets(state: DatasetUploaderState, dataset_name: str):
    # When loading from Firestore, we can clear the temporary cache
    # because Firestore should now (eventually) have the items.
    # However, for immediate consistency, we might want to MERGE them or just clear 
    # if we assume Firestore is slow.
    # Strategy: Clear cache, but if Firestore is missing recent items, they might be lost from view temporarily.
    # Better Strategy: Just fetching from Firestore is the "Ground Truth".
    # The cache is ONLY for "Pending/Recent" that might not be in Firestore yet.
    # But filtering duplicates is hard without IDs. We have IDs now!
    
    # 1. Fetch from Firestore
    items = get_media_by_dataset(dataset_name)
    
    # 2. Clear cache (assuming we want to reset on full refresh)
    # If the user hits "Refresh", they expect a sync with DB.
    clear_cache(dataset_name)
    
    state.asset_count = len(items)
    # Serialize to dicts
    assets_dicts = []
    for item in items:
        d = asdict(item)
        if d.get("timestamp") and isinstance(d["timestamp"], datetime.datetime):
            d["timestamp"] = d["timestamp"].isoformat()
        assets_dicts.append(d)
    state.dataset_assets = assets_dicts

def on_existing_dataset_change(e: me.SelectSelectionChangeEvent):
    state = me.state(DatasetUploaderState)
    state.selected_existing_dataset = e.value
    if state.selected_existing_dataset:
        load_dataset_assets(state, state.selected_existing_dataset)

def on_dataset_name_input(e: me.InputEvent):
    state = me.state(DatasetUploaderState)
    state.dataset_name = e.value

def on_description_input(e: me.InputEvent):
    state = me.state(DatasetUploaderState)
    state.description = e.value

def on_file_upload(e: me.UploadEvent):
    state = me.state(DatasetUploaderState)
    app_state = me.state(AppState)
    
    target_dataset_name = ""
    
    
    if state.is_new_dataset:
        if not state.dataset_name:
            state.upload_status = "Error: Please enter a Dataset Name first."
            return
        target_dataset_name = state.dataset_name
    else:
        if not state.selected_existing_dataset:
            state.upload_status = "Error: Please select an Existing Project first."
            return
        target_dataset_name = state.selected_existing_dataset

    uploaded_files = e.files if hasattr(e, "files") and e.files else [e.file]
    
    state.is_uploading = True
    success_count = 0
    
    for i, file in enumerate(uploaded_files):
        print(f"[DEBUG] Processing file {i+1}/{len(uploaded_files)}: {file.name}")
        state.upload_status = f"Uploading {file.name} ({i + 1}/{len(uploaded_files)})..."
        
        try:
            if state.is_new_dataset:
                # 1. Save Dataset Metadata (only if new)
                save_dataset(target_dataset_name, state.description)

            # 2. Upload File to GCS
            file_content = file.read()
            gcs_uri = store_to_gcs(
                folder=f"datasets/{target_dataset_name}",
                file_name=file.name,
                mime_type=file.mime_type,
                contents=file_content
            )

            # 3. Create MediaItem
            new_id = add_media_item(
                user_email=app_state.user_email,
                gcsuri=gcs_uri,
                mime_type=file.mime_type,
                dataset_name=target_dataset_name,
                media_type="image", 
                status="complete",
                prompt="Uploaded Asset for Dataset",
                mode="dataset_upload",
            )

            if new_id:
                 new_asset = {
                     "id": new_id,
                     "dataset_name": target_dataset_name,
                     "gcsuri": gcs_uri,
                     "mime_type": file.mime_type,
                     "media_type": "image",
                     "status": "complete",
                     "timestamp": datetime.datetime.now().isoformat()
                 }
                 add_to_cache(target_dataset_name, new_asset)
                 success_count += 1
                      
        except Exception as ex:
            print(f"[ERROR] Upload failed for {file.name}: {ex}")
            state.upload_status = f"Upload failed for {file.name}: {str(ex)}"
    
    if success_count > 0:
        cached = get_cached_uploads(target_dataset_name)
        cached_ids = {c['id'] for c in cached}
        existing_filtered = [a for a in state.dataset_assets if a.get('id') not in cached_ids]
        state.dataset_assets = cached + existing_filtered
        state.asset_count = len(state.dataset_assets)
        state.upload_status = f"Successfully uploaded {success_count} files."
    
    state.is_uploading = False
