# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Cartoon Studio - Nano Banana Pro backed generation."""

import mesop as me
from dataclasses import dataclass, field

from common.utils import create_display_url, https_url_to_gcs_uri
from common.storage import store_to_gcs
from common.analytics import track_model_call
from common.metadata import MediaItem, add_media_item_to_firestore
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from components.snackbar import snackbar
from components.image_thumbnail import image_thumbnail
from components.library.library_chooser_button import library_chooser_button
from models.gemini import generate_image_from_prompt_and_images
from state.state import AppState

# Constants
NANO_BANANA_PRO = "gemini-3-pro-image-preview"

@me.stateclass
class PageState:
    # Character Inputs
    character_uris: list[str] = field(default_factory=list)
    character_display_urls: list[str] = field(default_factory=list)
    
    # Panel/Setting Generation
    panel_description: str = ""
    panel_image_uri: str = ""
    panel_display_url: str = ""
    is_generating_panel: bool = False
    
    # Story Input
    story_text: str = ""
    
    # Final Generation
    is_generating_cartoon: bool = False
    cartoon_image_url: str = ""
    
    # UI State
    snackbar_message: str = ""
    show_snackbar: bool = False
    info_dialog_open: bool = False

@me.component
def _character_uploader():
    state = me.state(PageState)
    max_chars = 5
    
    with me.box(style=me.Style(margin=me.Margin(bottom=24))):
        me.text("1. Upload Characters (Max 5)", type="headline-6")
        with me.box(style=me.Style(display="flex", flex_direction="row", gap=16, flex_wrap="wrap")):
            # Existing Images
            for i, url in enumerate(state.character_display_urls):
                image_thumbnail(
                    image_uri=url,
                    index=i,
                    on_remove=on_remove_character,
                    icon_size=20
                )
            
            # Upload Slots
            if len(state.character_uris) < max_chars:
                with me.box(
                    style=me.Style(
                        width=100, height=100,
                        border=me.Border.all(me.BorderSide(width=1, style="dashed", color="#ccc")),
                        border_radius=8,
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        flex_direction="column"
                    )
                ):
                    me.uploader(
                        label="Upload",
                        on_upload=on_character_upload,
                        accepted_file_types=["image/jpeg", "image/png", "image/webp"],
                        multiple=True
                    )
                    library_chooser_button(
                        on_library_select=on_character_library_select,
                        button_type="icon",
                        key="char_lib"
                    )

@me.component
def _panel_generator():
    state = me.state(PageState)
    with me.box(style=me.Style(margin=me.Margin(bottom=24))):
        me.text("2. Generate Panel / Setting", type="headline-6")
        me.textarea(
            label="Describe the setting (e.g. Futuristic city classroom)",
            value=state.panel_description,
            on_blur=on_panel_desc_blur,
            style=me.Style(width="100%")
        )
        with me.box(style=me.Style(margin=me.Margin(top=16), display="flex", gap=16, align_items="center")):
            me.button(
                "Generate Setting", 
                on_click=generate_setting,
                type="stroked",
                disabled=state.is_generating_panel
            )
            if state.is_generating_panel:
                me.progress_spinner(diameter=20)
        
        if state.panel_display_url:
            with me.box(style=me.Style(margin=me.Margin(top=16))):
                me.image(
                    src=state.panel_display_url,
                    style=me.Style(max_width="100%", height=200, border_radius=8, object_fit="cover")
                )

@me.component
def _story_input():
    state = me.state(PageState)
    with me.box(style=me.Style(margin=me.Margin(bottom=24))):
        me.text("3. Story Input", type="headline-6")
        me.textarea(
            label="Enter the story for this panel...",
            value=state.story_text,
            on_blur=on_story_blur,
            style=me.Style(width="100%", min_height=100)
        )

@me.component
def _final_generation():
    state = me.state(PageState)
    
    disabled = not (state.character_uris and state.story_text)
    
    with me.box(style=me.Style(margin=me.Margin(top=32), border=me.Border(top=me.BorderSide(width=1, color="#eee", style="solid")), padding=me.Padding(top=32))):
        me.text("4. Make Cartoon", type="headline-6")
        
        me.button(
            "Generate Cartoon Panel",
            on_click=generate_cartoon,
            type="raised",
            disabled=state.is_generating_cartoon or disabled
        )
        
        if state.is_generating_cartoon:
            with me.box(style=me.Style(margin=me.Margin(top=16))):
                me.progress_spinner()
                me.text("Generating cartoon...")
        
        if state.cartoon_image_url:
            with me.box(style=me.Style(margin=me.Margin(top=24))):
                me.image(
                    src=state.cartoon_image_url,
                    style=me.Style(width="100%", border_radius=12, box_shadow="0 4px 12px rgba(0,0,0,0.1)")
                )

def cartoon_page_content():
    state = me.state(PageState)
    
    if state.info_dialog_open:
        # Simple info dialog
        pass 

    with page_frame():
        header("Cartoon Studio", "menu_book")
        
        with me.box(style=me.Style(display="flex", gap=24, padding=me.Padding.all(24))):
            # Left Column: Inputs
            with me.box(style=me.Style(flex_grow=1, flex_basis="400px")):
                _character_uploader()
                _panel_generator()
                _story_input()
                _final_generation()
            
            # Right Column: Preview could go here, but final gen is inline for now
            
        snackbar(is_visible=state.show_snackbar, label=state.snackbar_message)

def on_character_upload(e: me.UploadEvent):
    state = me.state(PageState)
    if len(state.character_uris) >= 5:
        return
    
    for file in e.files:
        if len(state.character_uris) >= 5: break
        gcs_uri = store_to_gcs("cartoon_chars", file.name, file.mime_type, file.getvalue())
        state.character_uris.append(gcs_uri)
        state.character_display_urls.append(create_display_url(gcs_uri))
    yield

def on_character_library_select(e):
    state = me.state(PageState)
    if len(state.character_uris) >= 5: return
    state.character_uris.append(e.gcs_uri)
    state.character_display_urls.append(create_display_url(e.gcs_uri))
    yield

def on_remove_character(e: me.ClickEvent):
    state = me.state(PageState)
    idx = int(e.key)
    if 0 <= idx < len(state.character_uris):
        state.character_uris.pop(idx)
        state.character_display_urls.pop(idx)
    yield

def on_panel_desc_blur(e: me.InputEvent):
    me.state(PageState).panel_description = e.value

def on_story_blur(e: me.InputEvent):
    me.state(PageState).story_text = e.value

def generate_setting(e: me.ClickEvent):
    state = me.state(PageState)
    if not state.panel_description: return
    
    state.is_generating_panel = True
    yield
    
    try:
        # Using Nano Banana Pro for setting as well, or could use Imagen
        prompt = f"Background setting for a cartoon: {state.panel_description}. High quality, detailed background art only, no characters."
        uris, _, _, _ = generate_image_from_prompt_and_images(
            prompt=prompt,
            images=[],
            aspect_ratio="16:9",
            model_name=NANO_BANANA_PRO
        )
        if uris:
            state.panel_image_uri = uris[0]
            state.panel_display_url = create_display_url(uris[0])
    except Exception as ex:
        state.snackbar_message = f"Error: {ex}"
        state.show_snackbar = True
    finally:
        state.is_generating_panel = False
        yield

def generate_cartoon(e: me.ClickEvent):
    state = me.state(PageState)
    app_state = me.state(AppState)
    
    state.is_generating_cartoon = True
    state.cartoon_image_url = ""
    yield
    
    try:
        # Construct Prompt
        chars_text = "the provided character(s)"
        setting_text = f"the setting '{state.panel_description}'" if state.panel_description else "a suitable background"
        
        prompt = f"""
        Create a cartoon panel based on this story:
        "{state.story_text}"
        
        Using {chars_text} in {setting_text}.
        Maintain character consistency and style.
        """
        
        input_images = list(state.character_uris)
        if state.panel_image_uri:
            input_images.append(state.panel_image_uri)
            
        uris, exec_time, _, _ = generate_image_from_prompt_and_images(
            prompt=prompt,
            images=input_images,
            aspect_ratio="16:9",
            model_name=NANO_BANANA_PRO
        )
        
        if uris:
            state.cartoon_image_url = create_display_url(uris[0])
            
            # Save to Library
            item = MediaItem(
                gcs_uris=uris,
                prompt=prompt,
                mime_type="image/png",
                user_email=app_state.user_email,
                source_images_gcs=input_images,
                comment="Cartoon Studio Generation",
                model=NANO_BANANA_PRO,
                generation_time=exec_time
            )
            add_media_item_to_firestore(item)
            
    except Exception as ex:
        state.snackbar_message = f"Error: {ex}"
        state.show_snackbar = True
        print(ex)
    finally:
        state.is_generating_cartoon = False
        yield

@me.page(path="/cartoon", title="Cartoon Studio")
def page():
    with page_scaffold(page_name="cartoon"):
        cartoon_page_content()
