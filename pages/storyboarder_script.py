import mesop as me
from models import gemini
from components.header import header
from components.page_scaffold import page_frame, page_scaffold

@me.stateclass
class StoryboardState:
    prompt: str = ""
    script: str = ""
    is_loading: bool = False

def on_prompt_input(e: me.InputBlurEvent):
    state = me.state(StoryboardState)
    state.prompt = e.value

def on_generate_click(e: me.ClickEvent):
    state = me.state(StoryboardState)
    state.is_loading = True
    yield
    
    try:
        state.script = gemini.generate_script(state.prompt)
    except Exception as e:
        state.script = f"Error generating script: {str(e)}"
    finally:
        state.is_loading = False
        yield

@me.page(path="/storyboarder_script")
def storyboard_page():
    state = me.state(StoryboardState)
    
    with page_scaffold(page_name="Storyboard"):
        with page_frame():
            header("Storyboard", "movie_creation")
            
            with me.box(style=me.Style(display="flex", flex_direction="column", padding=me.Padding.all(24), gap=24)):
                me.text("Create your Storyboard & Script", style=me.Style(font_size=20, font_weight="bold"))
                
                with me.box(style=me.Style(width="100%", border=me.Border.all(me.BorderSide(width=1, color="#e0e0e0", style="solid")), border_radius=8, padding=me.Padding.all(16))):
                    me.textarea(
                        label="Story Concept",
                        placeholder="A young wizard discovers a hidden portal...",
                        on_blur=on_prompt_input,
                        value=state.prompt,
                        style=me.Style(width="100%", margin=me.Margin(bottom=16), min_height=100),
                    )
                
                with me.box(style=me.Style(display="flex", justify_content="flex-end")):
                    me.button(
                        "Generate Script",
                        on_click=on_generate_click,
                        type="flat",
                        color="primary",
                        disabled=state.is_loading,
                        style=me.Style(background="#1a73e8", color="white")
                    )
            
            if state.is_loading:
                with me.box(style=me.Style(display="flex", justify_content="center", padding=me.Padding.all(24))):
                    me.progress_spinner()
                
            if state.script:
                with me.box(
                    style=me.Style(
                        background="#f8f9fa",
                        padding=me.Padding.all(24),
                        border_radius=8,
                        border=me.Border.all(me.BorderSide(width=1, color="#e0e0e0", style="solid")),
                        width="100%",
                    )
                ):
                    me.markdown(state.script)
