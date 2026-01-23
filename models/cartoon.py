import mesop as me
from common.analytics import track_model_call
from config.default import Default
from models.model_setup import GeminiModelSetup
from google.genai import types
from models.image_models import generate_images

cfg = Default()
client = GeminiModelSetup.init()

def analyze_conte(conte_uri: str) -> str:
    """
    Analyzes a conte/sketch image and generates a detailed visual description
    suitable for image generation prompts.
    """
    model_name = cfg.GEMINI_IMAGE_GEN_MODEL # Or a specific vision model
    # Using Gemini 1.5 Pro or similar
    
    prompt = """
    Analyze this sketch/conte for a cartoon. Describe the scene, characters, composition, and action in detail.
    Focus on visual elements that should be present in the final high-quality cartoon frame.
    Ignore rough sketch artifacts; describe the intended scene.
    
    IMPORTANT: Any RED lines or strokes in the image are NOT part of the visual scene. They are ANNOTATIONS or INSTRUCTIONS describing the action, movement, or context.
    - Do NOT include "red lines" in the visual description.
    - DO use the meaning of the red annotations to enhance the scene description (e.g., if a red arrow points up, describe the character jumping or moving up).
    """
    
    try:
        conte_part = types.Part.from_uri(file_uri=conte_uri, mime_type="image/png")
        
        with track_model_call(model_name=model_name, task="analyze_conte"):
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt, conte_part],
                config=types.GenerateContentConfig(
                    temperature=0.4,
                )
            )
        return response.text
    except Exception as e:
        print(f"Error analyzing conte: {e}")
        return ""

from common.metadata import get_media_by_dataset

def analyze_dataset_style(dataset_name: str) -> str:
    """
    Analyzes the visual style of a dataset by looking at its recent images.
    Returns a style description string.
    """
    try:
        # Fetch up to 3 recent images
        items = get_media_by_dataset(dataset_name, limit=3)
        if not items:
            return "Modern High Quality Cartoon" # Default fallback
            
        image_parts = []
        for item in items:
            uri = None
            if item.gcsuri:
                uri = item.gcsuri
            elif item.gcs_uris:
                uri = item.gcs_uris[0]
            
            if uri:
                try:
                    part = types.Part.from_uri(file_uri=uri, mime_type=item.mime_type or "image/png")
                    image_parts.append(part)
                except Exception:
                    continue
        
        if not image_parts:
            return "Modern High Quality Cartoon"

        prompt = """
        Analyze these images from a specific animation project.
        Describe their shared visual style in 2-3 sentences, focusing on:
        - Line quality (e.g. thick, thin, sketchy, clean, watercolor-like)
        - Color palette (e.g. vibrant, muted, pastel, noir, monochrome)
        - Shading/Lighting style
        - Overall artistic mood (e.g. Ghibli-esque, Disney-style, Anime, abstract)
        
        Provide ONLY the style description.
        """
        
        with track_model_call(model_name=cfg.GEMINI_IMAGE_GEN_MODEL, task="analyze_dataset_style"):
             response = client.models.generate_content(
                model=cfg.GEMINI_IMAGE_GEN_MODEL,
                contents=[prompt] + image_parts,
                config=types.GenerateContentConfig(temperature=0.4)
            )
        
        style = response.text.strip()
        print(f"Detected Style for {dataset_name}: {style}")
        return style
        
    except Exception as e:
        print(f"Error analyzing dataset style: {e}")
        return "Modern High Quality Cartoon"


def generate_cartoon_frame(description: str, dataset_name: str) -> str:
    """
    Generates a cartoon frame based on the description and dataset context.
    Returns the GCS URI of the generated image.
    """
    # 1. Analyze Dataset Style
    style_description = analyze_dataset_style(dataset_name)
    
    # 2. Construct the final prompt
    prompt = f"""
    Create a high-quality cartoon frame.
    
    Target Visual Style:
    {style_description}
    
    Scene Description:
    {description}
    
    Dataset/Project Context: {dataset_name}
    
    Quality: Best quality, 4k, consistent with the target style.
    """
    
    # Call Imagen
    try:
        uris = generate_images(
            model=cfg.MODEL_IMAGEN, # Use Imagen 3
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="16:9", # Default for cartoons
            negative_prompt="bad anatomy, blurry, low resolution, sketch, wireframe, messy",
        )
        if uris.generated_images:
            return uris.generated_images[0].image.gcs_uri
    except Exception as e:
        print(f"Error generating cartoon: {e}")
    
    return ""
