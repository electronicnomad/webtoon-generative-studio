import mesop as me
from dataclasses import dataclass, field
from typing import List

from common.storage import store_to_gcs
from common.utils import create_display_url
from components.page_scaffold import page_scaffold, page_frame
from components.header import header
from components.cartoon.dataset_uploader import dataset_uploader
from components.image_thumbnail import image_thumbnail
from common.metadata import get_all_datasets, add_media_item, MediaItem, delete_media_item
from state.state import AppState
from models.cartoon import analyze_conte, generate_cartoon_frame, analyze_dataset_style

@dataclass
class CartoonProDetails:
    dataset_name: str = ""
    # We will add more fields later (conte_image, script, etc.)

@me.stateclass
class PageState:
    is_loading: bool = False
    datasets: List[dict] = field(default_factory=list)
    selected_dataset: str = ""
    dataset_items: List[MediaItem] = field(default_factory=list)
    conte_image_uri: str = ""
    conte_image_gcs_uri: str = ""
    generated_image_uri: str = ""
    prompt: str = ""

    
def on_delete_item_from_event(e: me.ClickEvent):
    """
    Handles deletion by extracting the item ID from the event key.
    Key format: 'btn_del_{item_id}'
    """
    key = e.key
    if not key or not key.startswith("btn_del_"):
        print(f"[ERROR] Invalid delete key: {key}")
        return

    item_id = key.replace("btn_del_", "")
    
    state = me.state(PageState)
    
    # Optimistic Update
    state.dataset_items = [item for item in state.dataset_items if item.id != item_id]
    
    try:
        delete_media_item(item_id)
    except Exception as ex:
        print(f"Error deleting item {item_id}: {ex}")

def on_load(e: me.LoadEvent):
    """Load available datasets."""
    state = me.state(PageState)
    state.is_loading = True
    yield
    
    try:
        # Fetch datasets
        raw_datasets = get_all_datasets()
        # Serialize datetimes for Mesop state
        for d in raw_datasets:
            for k, v in d.items():
                if hasattr(v, 'isoformat'):
                    d[k] = v.isoformat()
        state.datasets = raw_datasets
        
        if state.datasets:
            # Default to first one if available? Or let user select.
            pass
    except Exception as e:
        print(f"Error in cartoon_pro on_load: {e}")
        # Optionally set an error state to display to user
        
    state.is_loading = False
    yield

def on_dataset_change(e: me.SelectSelectionChangeEvent):
    state = me.state(PageState)
    state.selected_dataset = e.value
    _load_dataset_items(state)

def _load_dataset_items(state):
    # Load thumbnails for the selected dataset
    try:
        from common.metadata import get_media_by_dataset
        items = get_media_by_dataset(state.selected_dataset, limit=20)
        # Create a new list object to ensure reference change for state detection
        state.dataset_items = list(items)
    except Exception as ex:
        print(f"Error loading thumbnails: {ex}")
        import traceback
        traceback.print_exc()
        state.dataset_items = []

def on_conte_upload(e: me.UploadEvent):
    state = me.state(PageState)
    try:
        gcs_uri = store_to_gcs(
            folder="conte",
            file_name=e.file.name,
            mime_type=e.file.mime_type,
            contents=e.file.read()
        )
        state.conte_image_gcs_uri = gcs_uri
        state.conte_image_uri = create_display_url(gcs_uri)
    except Exception as ex:
        print(f"Error uploading conte: {ex}")
        pass

@me.page(
    path="/cartoon_pro",
    title="Cartoon Pro",
    on_load=on_load,
)
def page():
    with page_scaffold(page_name="cartoon_pro"):
        with page_frame():
            header("Cartoon Pro", "auto_stories")
            
            state = me.state(PageState)
            
            with me.box(style=me.Style(display="flex", flex_direction="row", gap=24, padding=me.Padding.all(16))):
                # Left Column: Configuration & Inputs
                with me.box(style=me.Style(flex_basis="40%", flex_grow=1, display="flex", flex_direction="column", gap=16, min_width=0)):
                    me.text("1. Select Dataset", type="headline-6")
                    
                    with me.box(style=me.Style(display="flex", align_items="center", gap=8)):
                        dataset_options = [
                            me.SelectOption(label=d["name"], value=d["name"]) 
                            for d in state.datasets
                        ]
                        
                        me.select(
                            label="Choose Project/Dataset",
                            options=dataset_options,
                            value=state.selected_dataset,
                            on_selection_change=on_dataset_change,
                            style=me.Style(flex_grow=1)
                        )
                        with me.content_button(type="icon", on_click=on_refresh_datasets):
                            me.tooltip(message="Refresh Datasets")
                            me.icon("refresh")
                    
                    # Thumbnails Preview
                    if state.dataset_items:
                        me.text(f"Recent {len(state.dataset_items)} items:", style=me.Style(font_size=12, color="#666"))
                        with me.box(style=me.Style(
                            display="flex", 
                            flex_direction="row", 
                            gap=8, 
                            overflow_x="auto", 
                            padding=me.Padding.all(8),
                            background="#f5f5f5",
                            border_radius=8,
                            border=me.Border.all(me.BorderSide(width=1, color="#e0e0e0")),
                            width="100%", # Ensure it doesn't exceed parent width
                            max_width="100%", # Force containment
                        )):
                            for index, item in enumerate(state.dataset_items):
                                uri = None
                                if item.thumbnail_uri:
                                    uri = item.thumbnail_uri
                                elif item.gcsuri:
                                    uri = create_display_url(item.gcsuri)
                                elif item.gcs_uris:
                                    uri = create_display_url(item.gcs_uris[0])
                                
                                if uri:
                                    # Use ID-based key to ensure Mesop tracks the item correctly
                                    # This fixes the "last item deleted" bug by ensuring the component is tied to the data ID, not the index.
                                    # Pass key directly to the component to ensure React/Mesop tracks it correctly at the component level
                                    image_thumbnail(
                                        key=f"thumb_{item.id}",
                                        image_uri=uri,
                                        index=index,
                                        on_remove=on_delete_item_from_event,
                                        title=item.id,
                                        icon_size=16,
                                        delete_button_key=f"btn_del_{item.id}"
                                    )

                    elif state.selected_dataset:
                        me.text("No reference images found.", style=me.Style(color="gray", font_size=12, font_style="italic"))



                    
                    # Collapsible or Separate Section for Uploading New Assets
                    with me.expansion_panel(title="Manage Datasets & Assets"):
                        dataset_uploader()
                    
                    me.divider()
                    
                    me.text("2. Upload Conte (Sketch)", type="headline-6")
                    me.uploader(
                        label="Upload Sketch/Conte",
                        accepted_file_types=["image/jpeg", "image/png"],
                        on_upload=on_conte_upload,
                        style=me.Style(width="100%")
                    )
                    
                    if state.conte_image_uri:
                        me.image(src=state.conte_image_uri, style=me.Style(height=200))
                
                # Right Column: Preview & Results
                with me.box(style=me.Style(flex_basis="60%", flex_grow=2, display="flex", flex_direction="column", gap=16)):
                    me.text("3. Generation", type="headline-6")
                    
                    if not state.selected_dataset:
                        me.text("Please select a dataset to start.", style=me.Style(color="gray"))
                    else:
                        me.text(f"Active Dataset: {state.selected_dataset}")
                        # Placeholder for Generation UI
                        disable_generate = not (state.selected_dataset and state.conte_image_uri)
                        me.button("Generate Cartoon", on_click=on_generate_click, type="flat", disabled=disable_generate)
                        
                        if state.is_loading:
                            me.progress_spinner()
                        
                        if state.generated_image_uri:
                            me.image(src=state.generated_image_uri, style=me.Style(width="100%", border_radius=8))
                        
                        if state.prompt:
                            with me.expansion_panel(title="Analysis & Prompt"):
                                me.text(state.prompt)

def on_refresh_datasets(e: me.ClickEvent):
    state = me.state(PageState)
    state.datasets = get_all_datasets()
    yield

def on_generate_click(e: me.ClickEvent):
    state = me.state(PageState)
    app_state = me.state(AppState)
    
    if not state.selected_dataset or not state.conte_image_gcs_uri:
        return

    state.is_loading = True
    yield

    try:
        # 1. Analyze Dataset Style First
        # Collect URIs from current dataset items to use as style reference
        reference_uris = []
        for item in state.dataset_items:
             if item.gcsuri:
                 reference_uris.append(item.gcsuri)
             elif item.gcs_uris:
                 reference_uris.append(item.gcs_uris[0])
        
        # Analyze style immediately to use in sketch interpretation
        style_description = analyze_dataset_style(state.selected_dataset, reference_image_uris=reference_uris)
        
        # 2. Analyze Conte (with Style Context)
        description = analyze_conte(state.conte_image_gcs_uri, style_description=style_description)
        print(f"Cartoon Pro Analysis: {description}")
        
        # Display the full logic to the user
        state.prompt = f"**Detected Style:**\n{style_description}\n\n**Scene Analysis:**\n{description}"

        # 3. Generate Frame
        # Pass these references and style to the generation function
        generated_gcs_uri = generate_cartoon_frame(
            description, 
            state.selected_dataset, 
            reference_image_uris=reference_uris,
            style_description=style_description
        )
        
        if generated_gcs_uri:
            state.generated_image_uri = create_display_url(generated_gcs_uri)
            
            # 3. Save to Library
            add_media_item(
                user_email=app_state.user_email,
                gcsuri=generated_gcs_uri,
                mime_type="image/jpeg", # Imagen output is usually jpeg or png
                dataset_name=state.selected_dataset,
                media_type="image",
                status="complete",
                prompt=description,
                comment="Generated via Cartoon Pro",
                mode="cartoon_pro",
                source_images_gcs=[state.conte_image_gcs_uri]
            )
            
    except Exception as ex:
        print(f"Error generating cartoon: {ex}")
    
    state.is_loading = False
    yield
