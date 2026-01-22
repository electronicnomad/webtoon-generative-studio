import mesop as me
from dataclasses import dataclass, field
from typing import List

from common.storage import store_to_gcs
from common.utils import create_display_url
from components.page_scaffold import page_scaffold, page_frame
from components.header import header
from components.cartoon.dataset_uploader import dataset_uploader
from common.metadata import get_all_datasets, add_media_item
from state.state import AppState
from models.cartoon import analyze_conte, generate_cartoon_frame

@dataclass
class CartoonProDetails:
    dataset_name: str = ""
    # We will add more fields later (conte_image, script, etc.)

@me.stateclass
class PageState:
    is_loading: bool = False
    datasets: List[dict] = field(default_factory=list)
    selected_dataset: str = ""
    conte_image_uri: str = ""
    conte_image_gcs_uri: str = ""
    generated_image_uri: str = ""
    prompt: str = ""
    
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
                with me.box(style=me.Style(flex_basis="40%", flex_grow=1, display="flex", flex_direction="column", gap=16)):
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
        # 1. Analyze Conte
        description = analyze_conte(state.conte_image_gcs_uri)
        print(f"Cartoon Pro Analysis: {description}")
        state.prompt = description # For debug/display

        # 2. Generate Frame
        generated_gcs_uri = generate_cartoon_frame(description, state.selected_dataset)
        
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
