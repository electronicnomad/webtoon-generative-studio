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

def generate_cartoon_frame(description: str, dataset_name: str, style_description: str = "Modern High Quality Cartoon") -> str:
    """
    Generates a cartoon frame based on the description and dataset context.
    Returns the GCS URI of the generated image.
    """
    # Construct the final prompt
    prompt = f"""
    Create a high-quality cartoon frame.
    Style: {style_description}
    Dataset/Project: {dataset_name} (Conceptual context)
    
    Scene Description:
    {description}
    
    Quality: Best quality, 4k, vibrant colors, clean lines.
    """
    
    # Call Imagen
    # Using Imagen 3 (via generate_images from image_models)
    # We default to 1 image for now
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
