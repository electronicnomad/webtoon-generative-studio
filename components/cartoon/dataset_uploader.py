import mesop as me
from dataclasses import dataclass
from typing import Callable, Optional
import datetime

from common.storage import store_to_gcs
from common.metadata import add_media_item, save_dataset
from state.state import AppState
@dataclass
class DatasetUploaderState:
    dataset_name: str = ""
    description: str = ""
    is_uploading: bool = False
    upload_status: str = ""

@me.component
def dataset_uploader():
    """
    Component to upload assets to a specific dataset.
    """
    state = me.state(DatasetUploaderState)
    app_state = me.state(AppState)

    with me.box(style=me.Style(display="flex", flex_direction="column", gap=16, border=me.Border.all(me.BorderSide(width=1, color="#e0e0e0")), padding=me.Padding.all(16), border_radius=8)):
        me.text("Add to Dataset", type="headline-6")
        
        me.input(
            label="Dataset Name (e.g. 'Project Alpha')",
            value=state.dataset_name,
            on_input=on_dataset_name_input,
            style=me.Style(width="100%")
        )
        
        me.textarea(
            label="Description (Optional context for this dataset)",
            value=state.description,
            on_input=on_description_input,
            style=me.Style(width="100%")
        )

        me.uploader(
            label="Upload Asset (Image)",
            accepted_file_types=["image/jpeg", "image/png", "image/webp"],
            on_upload=on_file_upload,
            style=me.Style(width="100%")
        )

        if state.is_uploading:
            me.progress_spinner()
        
        if state.upload_status:
            me.text(state.upload_status)

def on_dataset_name_input(e: me.InputEvent):
    state = me.state(DatasetUploaderState)
    state.dataset_name = e.value

def on_description_input(e: me.InputEvent):
    state = me.state(DatasetUploaderState)
    state.description = e.value

def on_file_upload(e: me.UploadEvent):
    state = me.state(DatasetUploaderState)
    app_state = me.state(AppState)
    
    if not state.dataset_name:
        state.upload_status = "Error: Please enter a Dataset Name first."
        return

    state.is_uploading = True
    state.upload_status = "Uploading..."
    yield

    try:
        # 1. Save Dataset Metadata (create/update)
        save_dataset(state.dataset_name, state.description)

        # 2. Upload File to GCS
        # We'll use a specific folder for datasets: `datasets/{dataset_name}/{filename}`
        file_content = e.file.read()
        gcs_uri = store_to_gcs(
            folder=f"datasets/{state.dataset_name}",
            file_name=e.file.name,
            mime_type=e.file.mime_type,
            contents=file_content
        )

        # 3. Create MediaItem
        add_media_item(
            user_email=app_state.user_email,
            gcsuri=gcs_uri,
            mime_type=e.file.mime_type,
            dataset_name=state.dataset_name,
            media_type="image", # Assumption, could be inferred
            status="complete",
            prompt="Uploaded Asset for Dataset",
            mode="dataset_upload",
        )

        state.upload_status = f"Successfully uploaded {e.file.name} to {state.dataset_name}"
             
    except Exception as ex:
        state.upload_status = f"Upload failed: {str(ex)}"
    
    state.is_uploading = False
    yield
