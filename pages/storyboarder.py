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
"""Storyboarder Workflow Page."""

import time
import uuid
import datetime
import mesop as me

from common.analytics import log_ui_click, track_model_call
from common.storage import store_to_gcs
from common.utils import create_display_url, https_url_to_gcs_uri
from common.metadata import MediaItem, add_media_item_to_firestore
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from components.snackbar import snackbar
from components.dialog import dialog
from config.default import Default as cfg
from models.gemini import generate_image_from_prompt_and_images, describe_image

from state.storyboarder_state import PageState
from state.state import AppState

@me.page(
    path="/storyboarder",
    title="Storyboarder - Webtoon Generator",
)
def page():
    with page_scaffold(page_name="storyboarder"):
        with page_frame():
            header("Storyboard Pro (Image and Video)", "movie_filter")
            storyboarder_content()

def storyboarder_content():
    state = me.state(PageState)
    
    snackbar(is_visible=state.show_snackbar, label=state.snackbar_message)

    with me.box(style=me.Style(display="flex", flex_direction="column", gap=24, padding=me.Padding.all(24))):
        
        # --- Input Section ---
        with me.box(style=me.Style(display="flex", flex_direction="column", gap=16, width="100%", max_width="800px", margin=me.Margin.symmetric(horizontal="auto"))):
            me.text("Create a video storyboard from a prompt.", type="headline-5")
            
            me.textarea(
                label="Storyboard Prompt",
                value=state.prompt,
                on_blur=on_prompt_blur,
                rows=3,
                style=me.Style(width="100%")
            )
            
            with me.box(style=me.Style(display="flex", gap=16, align_items="center")):
                me.select(
                    label="Aspect Ratio",
                    value=state.aspect_ratio,
                    options=[
                        me.SelectOption(label="16:9", value="16:9"),
                        me.SelectOption(label="9:16", value="9:16"),
                        me.SelectOption(label="1:1", value="1:1"),
                    ],
                    on_selection_change=on_aspect_ratio_change
                )
                
                me.button(
                    "Generate Storyboard Images",
                    on_click=on_generate_images_click,
                    type="raised",
                    disabled=state.is_generating_images or not state.prompt
                )
                
                if state.is_generating_images:
                    me.progress_spinner(diameter=24)

        # --- Image Results Section ---
        if state.generated_image_urls:
            me.divider()
            me.text("Storyboard Frames", type="headline-6")
            
            with me.box(style=me.Style(display="flex", flex_wrap="wrap", gap=16, justify_content="center")):
                for url in state.generated_image_urls:
                    me.image(
                        src=url,
                        style=me.Style(height="200px", border_radius=8, border=me.Border.all(me.BorderSide(width=1, color="#ccc")))
                    )
            



# --- Event Handlers ---

def on_prompt_blur(e: me.InputEvent):
    state = me.state(PageState)
    state.prompt = e.value

def on_aspect_ratio_change(e: me.SelectSelectionChangeEvent):
    state = me.state(PageState)
    state.aspect_ratio = e.value

def on_generate_images_click(e: me.ClickEvent):
    state = me.state(PageState)
    app_state = me.state(AppState)
    state.is_generating_images = True
    state.generated_image_urls = []
    state.generated_image_gcs_uris = []
    state.image_captions = []
    state.final_video_display_url = "" # Reset video
    yield
    
    try:
        gcs_uris, _, captions, _ = generate_image_from_prompt_and_images(
            prompt=state.prompt,
            images=[],
            aspect_ratio=state.aspect_ratio,
            gcs_folder="storyboard_images",
        )
        
        # If we only got 1, let's loop to get more.
        if len(gcs_uris) < 4:
            for _ in range(4 - len(gcs_uris)):
                new_uris, _, new_captions, _ = generate_image_from_prompt_and_images(
                    prompt=state.prompt,
                    images=[],
                    aspect_ratio=state.aspect_ratio,
                    gcs_folder="storyboard_images"
                )
                gcs_uris.extend(new_uris)
                captions.extend(new_captions)
        
        state.generated_image_gcs_uris = gcs_uris[:4] # Limit to 4
        state.image_captions = captions[:4]
        state.generated_image_urls = [create_display_url(uri) for uri in state.generated_image_gcs_uris]
        
        # Save generated storyboard images to Library
        media_item = MediaItem(
            id=str(uuid.uuid4()),
            user_email=app_state.user_email,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            media_type="image",
            mime_type="image/png",
            mode="Storyboarder",
            gcs_uris=state.generated_image_gcs_uris,
            thumbnail_uri=state.generated_image_gcs_uris[0] if state.generated_image_gcs_uris else "",
            prompt=state.prompt,
            comment="Generated by Storyboarder",
            captions=state.image_captions,
        )
        add_media_item_to_firestore(media_item)
        
        state.snackbar_message = "Storyboard images saved to library!"
        state.show_snackbar = True
        
    except Exception as ex:
        state.snackbar_message = f"Error generating images: {ex}"
        state.show_snackbar = True
    finally:
        state.is_generating_images = False
        yield