import mesop as me
from common.analytics import track_model_call
from config.default import Default
from models.model_setup import GeminiModelSetup
from google.genai import types
from models.image_models import generate_images

cfg = Default()
client = GeminiModelSetup.init()

def analyze_conte(conte_uri: str, style_description: str = None) -> str:
    """
    Analyzes a conte/sketch image and generates a detailed visual description
    suitable for image generation prompts.
    """
    model_name = cfg.GEMINI_IMAGE_GEN_MODEL # Or a specific vision model
    # Using Gemini 1.5 Pro or similar
    
    style_context = ""
    if style_description:
        style_context = f"\n    TARGET VISUAL STYLE:\n    {style_description}\n    \n    Interpret the sketch so that the character design and mood MATCH this target style."

    prompt = f"""
    You are an expert visual director. Your task is to interpret this ROUGH SKETCH (conte) and write a detailed scene description for a high-quality illustration.
    {style_context}

    CRITICAL INSTRUCTIONS:
    1. **translate Stick Figures**: If the sketch shows stick figures or simple shapes, describe them as **real, fully-fleshed out characters** (e.g., "a young man in a business suit", "a woman in a coat"). DO NOT describe them as "stick figures", "sketches", or "drawings". Assume they are humans unless context implies otherwise.
    2. **Interpret Red Annotations**: Any RED lines, arrows, or text are DIRECTORS NOTES. 
       - Do NOT include red lines visually in the scene.
       - Do NOT transcribe the text of the notes into the visual description (e.g. if it says "don't laugh", describe the character looking serious or holding back laughter, do not ask for text "don't laugh" in the image).
    3. **Composition**: Describe the scene as a finished, professional wide-angle shot.
    
    Output ONLY the visual description of the final scene.
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

def analyze_dataset_style(dataset_name: str, reference_image_uris: list[str] = None) -> str:
    """
    Analyzes the visual style of a dataset by looking at its images.
    If reference_image_uris are provided, uses those. Otherwise fetches recent ones.
    Returns a style description string.
    """
    try:
        image_parts = []
        
        # 1. Use provided references if available
        if reference_image_uris:
            print(f"Analyzing style using {len(reference_image_uris)} provided reference images")
            for uri in reference_image_uris[:5]: # Limit to 5 max
                try:
                    part = types.Part.from_uri(file_uri=uri, mime_type="image/jpeg") # Defaulting to jpeg, model usually handles standard types
                    image_parts.append(part)
                except Exception:
                    continue
        
        # 2. Fallback to fetching from dataset if no specific refs provided (or failed)
        if not image_parts:
            # Fetch up to 3 recent images
            items = get_media_by_dataset(dataset_name, limit=3)
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
        Analyze the provided reference images to extract their DISTINCT VISUAL STYLE.
        
        OUTPUT FORMAT (Strictly follow this):
        POSITIVE_STYLE: <comma_separated_keywords_for_style>
        NEGATIVE_STYLE: <comma_separated_keywords_to_avoid_to_maintain_this_style>
        
        INSTRUCTIONS for POSITIVE_STYLE:
        - Be specific about the "Vibe" (e.g. "mature office drama", "gritty noir", "whimsical fantasy").
        - Describe line weight (e.g. "thin delicate lines", "bold rough contours").
        - Describe color grading (e.g. "desaturated muted tones", "vibrant pop colors", "sepia tint").
        - Describe anatomy (e.g. "realistic proportions", "exaggerated heads").
        
        INSTRUCTIONS for NEGATIVE_STYLE:
        - List things that would BREAK this style.
        - Example: If the style is "realistic", negative should include "anime big eyes, chibi, cartoonish exaggeration".
        - Example: If the style is "flat", negative should include "3d render, realistic shading, volumetric lighting".
        """
        
        with track_model_call(model_name=cfg.GEMINI_IMAGE_GEN_MODEL, task="analyze_dataset_style"):
             response = client.models.generate_content(
                model=cfg.GEMINI_IMAGE_GEN_MODEL,
                contents=[prompt] + image_parts,
                config=types.GenerateContentConfig(temperature=0.4)
            )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Error analyzing dataset style: {e}")
        return "POSITIVE_STYLE: Modern High Quality Cartoon\nNEGATIVE_STYLE: low quality"


def generate_cartoon_frame(description: str, dataset_name: str, reference_image_uris: list[str] = None, style_description: str = None) -> str:
    """
    Generates a cartoon frame based on the description and dataset context.
    Returns the GCS URI of the generated image.
    """
    # 1. Analyze Dataset Style (if not provided)
    if not style_description:
        style_description = analyze_dataset_style(dataset_name, reference_image_uris)
    
    # Parse Style Description
    positive_style = style_description
    negative_style = "stick figures, rough sketch, doodle, incomplete, text, speech bubbles, messy, low quality, bad anatomy, deformed fingers, photographic, realistic" # Default fallback
    
    if "POSITIVE_STYLE:" in style_description:
        try:
            parts = style_description.split("NEGATIVE_STYLE:")
            if len(parts) >= 1:
                positive_style = parts[0].replace("POSITIVE_STYLE:", "").strip()
            if len(parts) >= 2:
                # Add dynamic negative prompts to the default base
                dynamic_neg = parts[1].strip()
                negative_style = f"{negative_style}, {dynamic_neg}"
        except:
            pass
            
    # 2. Construct the final prompt
    # Sandwich strategy: Style -> Content -> Style keywords again
    prompt = f"""
    visual style: {positive_style}
    
    scene description: {description}
    
    style keywords: {positive_style}
    
    technical quality: best quality, 4k, high resolution, masterpiece
    
    NEGATIVE PROMPT:
    {negative_style}
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
