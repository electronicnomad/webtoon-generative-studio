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

"""This module provides functions for interacting with the Gemini model.

It includes functions for generating content, improving prompts, and generating
thoughts for prompt improvement. It also uses the `tenacity` library to
provide automatic retries with exponential backoff for the Gemini API calls,
which makes the application more resilient to transient errors.
"""

import time
import uuid
import requests
from typing import Dict, Optional, Any
from google.genai import types
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from common.analytics import analytics_logger, track_model_call
from common.storage import store_to_gcs
from config.default import Default
from models.character_consistency_models import (
    BestImage,
    FacialCompositeProfile,
    GeneratedPrompts,
)
from models.model_setup import ModelSetup
from models.prompts import (
    PROMPT_IMPROVEMENT_INSTRUCTIONS,
    PROMPT_IMPROVEMENT_PLANNING_INSTRUCTIONS,
)

cfg = Default()
client, model_id = ModelSetup.init()
MODEL_ID = model_id


@retry(
    wait=wait_exponential(
        multiplier=1, min=1, max=10
    ),  # Exponential backoff (1s, 2s, 4s... up to 10s)
    stop=stop_after_attempt(3),  # Stop after 3 attempts
    retry=retry_if_exception_type(Exception),  # Retry on all exceptions
    reraise=True,  # re-raise the last exception if all retries fail
)
def gemini_generate_content(system_prompt: str = "", prompt: str = "") -> str:
    """Invokes the Gemini model to generate content.

    This function sends a prompt to the Gemini model and returns the generated
    content. It can also accept an optional system prompt to guide the model's
    behavior.

    Args:
        system_prompt: An optional system prompt to guide the model.
        prompt: The main prompt to send to the model.

    Returns:
        The generated content as a string.
    """

    try:
        if system_prompt:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_modalities=["TEXT"],
                ),
            )
        else:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=GenerateContentConfig(
                    response_modalities=["TEXT"],
                ),
            )
        # page_state.prompt_response = response.text
        print(f"success! {response.text}")
        return response.text
    except Exception as e:
        print(f"error: {e}")
        raise  # Re-raise the exception for tenacity to handle


@retry(
    wait=wait_exponential(
        multiplier=1, min=1, max=10
    ),  # Exponential backoff (1s, 2s, 4s... up to 10s)
    stop=stop_after_attempt(3),  # Stop after 3 attempts
    retry=retry_if_exception_type(Exception),  # Retry on all exceptions
    reraise=True,  # re-raise the last exception if all retries fail
)
def gemini_improve_this_prompt(
    system_prompt: str = "",
    prompt: str = "",
    basic_instructions: str = "",
    plan: str = "",
) -> str:
    """Improves a prompt using the Gemini model.

    This function takes a prompt, an optional system prompt, basic instructions,
    and a plan, and then uses the Gemini model to generate an improved version
    of the prompt.

    Args:
        system_prompt: An optional system prompt to guide the model.
        prompt: The prompt to improve.
        basic_instructions: Basic instructions for the improvement.
        plan: The plan for improving the prompt.

    Returns:
        The improved prompt as a string.
    """

    improvement_prompt = PROMPT_IMPROVEMENT_INSTRUCTIONS.format(
        plan,
        f"{system_prompt} {prompt}",
        basic_instructions,
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=improvement_prompt,
            config=GenerateContentConfig(
                response_modalities=["TEXT"],
            ),
        )
        # page_state.prompt_response = response.text
        print(f"success! {response.text}")
        return response.text
    except Exception as e:
        print(f"error: {e}")
        raise  # Re-raise the exception for tenacity to handle


@retry(
    wait=wait_exponential(
        multiplier=1, min=1, max=10
    ),  # Exponential backoff (1s, 2s, 4s... up to 10s)
    stop=stop_after_attempt(3),  # Stop after 3 attempts
    retry=retry_if_exception_type(Exception),  # Retry on all exceptions
    reraise=True,  # re-raise the last exception if all retries fail
)
def gemini_thinking_thoughts(
    system_prompt: str = "", prompt: str = "", prompt_improvement_instructions: str = ""
) -> str:
    """Generates a plan for improving a prompt using the Gemini model.

    This function takes a prompt, an optional system prompt, and prompt
    improvement instructions, and then uses the Gemini model to generate a plan
    for improving the prompt.

    Args:
        system_prompt: An optional system_prompt to guide the model.
        prompt: The prompt to improve.
        prompt_improvement_instructions: Instructions for the improvement.

    Returns:
        The plan for improving the prompt as a string.
    """

    planning_prompt = PROMPT_IMPROVEMENT_PLANNING_INSTRUCTIONS.format(
        f"{system_prompt} {prompt}",
        prompt_improvement_instructions,
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=planning_prompt,
            config=GenerateContentConfig(
                response_modalities=["TEXT"],
            ),
        )
        # page_state.prompt_response = response.text
        print(f"success! {response.text}")
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"error: {e}")
        raise  # Re-raise the exception for tenacity to handle


def generate_image_from_prompt_and_images(
    prompt: str,
    images: list[str],
    aspect_ratio: str,
    gcs_folder: str = "generated_images",
    file_prefix: str = "image",
    candidate_count: int = 1,
    image_size: Optional[str] = None,
    use_search: bool = False,
) -> tuple[list[str], float, list[str], Optional[Dict[str, Any]]]:
    """Generates images from a prompt and a list of images."""
    start_time = time.time()
    model_name = cfg.GEMINI_IMAGE_GEN_MODEL

    parts = [types.Part.from_text(text=prompt)]
    for image_uri in images:
        parts.append(types.Part.from_uri(file_uri=image_uri, mime_type="image/png"))

    contents = [types.Content(role="user", parts=parts)]

    http_options = None
    if cfg.GEMINI_IMAGE_GEN_API_BASE_URL:
        http_options = {"base_url": cfg.GEMINI_IMAGE_GEN_API_BASE_URL}

    # Initialize client for image generation (possibly different location)
    client_img, _ = ModelSetup.init(
        location=cfg.GEMINI_IMAGE_GEN_LOCATION,
        http_options=http_options,
    )

    analytics_logger.info(
        f"Generating image with model: {model_name}, aspect_ratio: {aspect_ratio}, num_images: {len(images)}, image_size: {image_size}, use_search: {use_search}"
    )
    for i, img in enumerate(images):
        analytics_logger.info(f"  Image {i}: {img}")

    image_config_args = {"aspect_ratio": aspect_ratio}
    if image_size:
        image_config_args["image_size"] = image_size

    tools = []
    if use_search:
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    with track_model_call(
        model_name=model_name,
        aspect_ratio=aspect_ratio,
        num_images=len(images),
    ):
        response = client_img.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(**image_config_args),
                tools=tools if tools else None,
            ),
        )

    end_time = time.time()
    execution_time = end_time - start_time

    gcs_uris = []
    captions = []
    current_text_buffer = ""
    grounding_info = None

    if response.candidates:
        candidate = response.candidates[0]
        if candidate.grounding_metadata:
            try:
                grounding_info = candidate.grounding_metadata.model_dump()
            except Exception as e:
                analytics_logger.warning(f"Failed to extract grounding metadata: {e}")

        if candidate.content and candidate.content.parts:
            analytics_logger.info(
                f"generate_image_from_prompt_and_images: {len(candidate.content.parts)} parts"
            )
            for i, part in enumerate(candidate.content.parts):
                if hasattr(part, "text") and part.text:
                    analytics_logger.info(
                        f"generate_image_from_prompt_and_images (text): {part.text}"
                    )
                    current_text_buffer += part.text
                
                if hasattr(part, "inline_data") and part.inline_data:
                    mime_type = "image/png"
                    if (
                        hasattr(part.inline_data, "mime_type")
                        and part.inline_data.mime_type
                    ):
                        mime_type = part.inline_data.mime_type
                    gcs_uri = store_to_gcs(
                        folder=gcs_folder,
                        file_name=f"{file_prefix}_{uuid.uuid4()}_{i}.png",
                        mime_type=mime_type,
                        contents=part.inline_data.data,
                    )
                    gcs_uris.append(gcs_uri)
                    captions.append(current_text_buffer.strip())
                    current_text_buffer = "" 
    else:
        analytics_logger.warning("generate_image_from_prompt_and_images: no images")
    return gcs_uris, execution_time, captions, grounding_info


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def get_facial_composite_profile(image_bytes: bytes) -> FacialCompositeProfile:
    """Analyzes an image and returns a structured facial profile."""
    model_name = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL

    profile_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=FacialCompositeProfile.model_json_schema(),
        temperature=cfg.TEMP_FORENSIC_ANALYSIS,
    )
    profile_prompt_parts = [
        "You are a forensic analyst. Analyze the following image and extract a detailed, structured facial profile.",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    ]
    with track_model_call(model_name=model_name, task="get_facial_composite_profile"):
        response = client.models.generate_content(
            model=model_name, contents=profile_prompt_parts, config=profile_config
        )
    return FacialCompositeProfile.model_validate_json(response.text)


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def get_natural_language_description(profile: FacialCompositeProfile) -> str:
    """Generates a natural language description from a facial profile."""
    model_name = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL

    description_config = types.GenerateContentConfig(
        temperature=cfg.TEMP_DESCRIPTION_TRANSLATION
    )
    description_prompt = f"""
    Based on the following structured JSON data of a person's facial features, write a concise, natural language description suitable for an image generation model. Focus on key physical traits.

    JSON Profile:
    {profile.model_dump_json(indent=2)}
    """
    with track_model_call(
        model_name=model_name, task="get_natural_language_description"
    ):
        response = client.models.generate_content(
            model=model_name, contents=[description_prompt], config=description_config
        )
    return response.text.strip()


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def generate_final_scene_prompt(
    base_description: str, user_prompt: str
) -> GeneratedPrompts:
    """
    Generates a detailed, photorealistic prompt to place a described person
    in a novel scene.
    """
    model_name = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=GeneratedPrompts.model_json_schema(),
        temperature=cfg.TEMP_SCENE_GENERATION,
    )

    meta_prompt = f"""
    You are an expert prompt engineer for a text-to-image generation model.
    Your task is to create a detailed, photorealistic prompt that places a specific person into a new scene.

    **Person Description:**
    {base_description}

    **User's Desired Scene:**
    {user_prompt}

    **Instructions:**
    1.  Combine the person's description with the user's scene to create a single, coherent, and highly detailed prompt.
    2.  The final image should be photorealistic. Add photography keywords like lens type (e.g., 85mm), lighting (e.g., cinematic lighting, soft light), and composition.
    3.  Ensure the final prompt clearly describes the person performing the action or being in the scene requested by the user.
    4.  Generate a standard negative prompt to avoid common artistic flaws.
    """
    with track_model_call(model_name=model_name, task="generate_final_scene_prompt"):
        response = client.models.generate_content(
            model=model_name, contents=[meta_prompt], config=config
        )
    return GeneratedPrompts.model_validate_json(response.text)


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def select_best_image(
    real_image_bytes_list: list[bytes],
    generated_image_bytes_list: list[bytes],
    generated_image_gcs_uris: list[str],
) -> BestImage:
    """Selects the best generated image by comparing it against a set of real
    images.
    """
    model = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL
    config = types.GenerateContentConfig(
        # thinking_config=types.ThinkingConfig(thinking_budget=1024), # Disable thinking for now/flash
        response_mime_type="application/json",
        response_schema=BestImage.model_json_schema(),
        temperature=cfg.TEMP_BEST_IMAGE_SELECTION,
    )

    prompt_parts = [
        "Please analyze the following images. The first set of images are real photos of a person. The second set of images are AI-generated.",
        "Your task is to select the generated image that best represents the person from the real photos, focusing on facial and physical traits, not clothing or style.",
        "Provide the path of the best image and your reasoning.",
        "\n--- REAL IMAGES ---",
    ]

    for image_bytes in real_image_bytes_list:
        prompt_parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        )

    prompt_parts.append("\n--- GENERATED IMAGES ---")

    for i, image_bytes in enumerate(generated_image_bytes_list):
        prompt_parts.append(f"Image path: {generated_image_gcs_uris[i]}")
        prompt_parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        )

    with track_model_call(model_name=model, task="select_best_image"):
        response = client.models.generate_content(
            model=model, contents=prompt_parts, config=config
        )
    return BestImage.model_validate_json(response.text)


def generate_image_from_prompt_and_images(
    prompt: str,
    images: list[str],
    aspect_ratio: str,
    gcs_folder: str = "generated_images",
    file_prefix: str = "image",
    candidate_count: int = 1,
    image_size: Optional[str] = None,
    use_search: bool = False,
) -> tuple[list[str], float, list[str], Optional[Dict[str, Any]]]:
    """Generates images from a prompt and a list of images."""
    start_time = time.time()
    model_name = cfg.GEMINI_IMAGE_GEN_MODEL

    parts = [types.Part.from_text(text=prompt)]
    for image_uri in images:
        parts.append(types.Part.from_uri(file_uri=image_uri, mime_type="image/png"))

    contents = [types.Content(role="user", parts=parts)]

    http_options = None
    if cfg.GEMINI_IMAGE_GEN_API_BASE_URL:
        http_options = {"base_url": cfg.GEMINI_IMAGE_GEN_API_BASE_URL}

    # Initialize client for image generation (possibly different location)
    client_img, _ = ModelSetup.init(
        location=cfg.GEMINI_IMAGE_GEN_LOCATION,
        http_options=http_options,
    )

    analytics_logger.info(
        f"Generating image with model: {model_name}, aspect_ratio: {aspect_ratio}, num_images: {len(images)}, image_size: {image_size}, use_search: {use_search}"
    )
    for i, img in enumerate(images):
        analytics_logger.info(f"  Image {i}: {img}")

    image_config_args = {"aspect_ratio": aspect_ratio}
    if image_size:
        image_config_args["image_size"] = image_size

    tools = []
    if use_search:
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    with track_model_call(
        model_name=model_name,
        aspect_ratio=aspect_ratio,
        num_images=len(images),
    ):
        response = client_img.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(**image_config_args),
                tools=tools if tools else None,
            ),
        )

    end_time = time.time()
    execution_time = end_time - start_time

    gcs_uris = []
    captions = []
    current_text_buffer = ""
    grounding_info = None

    if response.candidates:
        candidate = response.candidates[0]
        if candidate.grounding_metadata:
            try:
                grounding_info = candidate.grounding_metadata.model_dump()
            except Exception as e:
                analytics_logger.warning(f"Failed to extract grounding metadata: {e}")

        if candidate.content and candidate.content.parts:
            analytics_logger.info(
                f"generate_image_from_prompt_and_images: {len(candidate.content.parts)} parts"
            )
            for i, part in enumerate(candidate.content.parts):
                if hasattr(part, "text") and part.text:
                    analytics_logger.info(
                        f"generate_image_from_prompt_and_images (text): {part.text}"
                    )
                    current_text_buffer += part.text
                
                if hasattr(part, "inline_data") and part.inline_data:
                    mime_type = "image/png"
                    if (
                        hasattr(part.inline_data, "mime_type")
                        and part.inline_data.mime_type
                    ):
                        mime_type = part.inline_data.mime_type
                    gcs_uri = store_to_gcs(
                        folder=gcs_folder,
                        file_name=f"{file_prefix}_{uuid.uuid4()}_{i}.png",
                        mime_type=mime_type,
                        contents=part.inline_data.data,
                    )
                    gcs_uris.append(gcs_uri)
                    captions.append(current_text_buffer.strip())
                    current_text_buffer = "" 
    else:
        analytics_logger.warning("generate_image_from_prompt_and_images: no images")
    return gcs_uris, execution_time, captions, grounding_info


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def get_facial_composite_profile(image_bytes: bytes) -> FacialCompositeProfile:
    """Analyzes an image and returns a structured facial profile."""
    model_name = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL

    profile_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=FacialCompositeProfile.model_json_schema(),
        temperature=cfg.TEMP_FORENSIC_ANALYSIS,
    )
    profile_prompt_parts = [
        "You are a forensic analyst. Analyze the following image and extract a detailed, structured facial profile.",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    ]
    with track_model_call(model_name=model_name, task="get_facial_composite_profile"):
        response = client.models.generate_content(
            model=model_name, contents=profile_prompt_parts, config=profile_config
        )
    return FacialCompositeProfile.model_validate_json(response.text)


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def get_natural_language_description(profile: FacialCompositeProfile) -> str:
    """Generates a natural language description from a facial profile."""
    model_name = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL

    description_config = types.GenerateContentConfig(
        temperature=cfg.TEMP_DESCRIPTION_TRANSLATION
    )
    description_prompt = f"""
    Based on the following structured JSON data of a person's facial features, write a concise, natural language description suitable for an image generation model. Focus on key physical traits.

    JSON Profile:
    {profile.model_dump_json(indent=2)}
    """
    with track_model_call(
        model_name=model_name, task="get_natural_language_description"
    ):
        response = client.models.generate_content(
            model=model_name, contents=[description_prompt], config=description_config
        )
    return response.text.strip()


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def generate_final_scene_prompt(
    base_description: str, user_prompt: str
) -> GeneratedPrompts:
    """
    Generates a detailed, photorealistic prompt to place a described person
    in a novel scene.
    """
    model_name = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=GeneratedPrompts.model_json_schema(),
        temperature=cfg.TEMP_SCENE_GENERATION,
    )

    meta_prompt = f"""
    You are an expert prompt engineer for a text-to-image generation model.
    Your task is to create a detailed, photorealistic prompt that places a specific person into a new scene.

    **Person Description:**
    {base_description}

    **User's Desired Scene:**
    {user_prompt}

    **Instructions:**
    1.  Combine the person's description with the user's scene to create a single, coherent, and highly detailed prompt.
    2.  The final image should be photorealistic. Add photography keywords like lens type (e.g., 85mm), lighting (e.g., cinematic lighting, soft light), and composition.
    3.  Ensure the final prompt clearly describes the person performing the action or being in the scene requested by the user.
    4.  Generate a standard negative prompt to avoid common artistic flaws.
    """
    with track_model_call(model_name=model_name, task="generate_final_scene_prompt"):
        response = client.models.generate_content(
            model=model_name, contents=[meta_prompt], config=config
        )
    return GeneratedPrompts.model_validate_json(response.text)


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def select_best_image(
    real_image_bytes_list: list[bytes],
    generated_image_bytes_list: list[bytes],
    generated_image_gcs_uris: list[str],
) -> BestImage:
    """Selects the best generated image by comparing it against a set of real
    images.
    """
    model = cfg.CHARACTER_CONSISTENCY_GEMINI_MODEL
    config = types.GenerateContentConfig(
        # thinking_config=types.ThinkingConfig(thinking_budget=1024), # Disable thinking for now/flash
        response_mime_type="application/json",
        response_schema=BestImage.model_json_schema(),
        temperature=cfg.TEMP_BEST_IMAGE_SELECTION,
    )

    prompt_parts = [
        "Please analyze the following images. The first set of images are real photos of a person. The second set of images are AI-generated.",
        "Your task is to select the generated image that best represents the person from the real photos, focusing on facial and physical traits, not clothing or style.",
        "Provide the path of the best image and your reasoning.",
        "\n--- REAL IMAGES ---",
    ]

    for image_bytes in real_image_bytes_list:
        prompt_parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        )

    prompt_parts.append("\n--- GENERATED IMAGES ---")

    for i, image_bytes in enumerate(generated_image_bytes_list):
        prompt_parts.append(f"Image path: {generated_image_gcs_uris[i]}")
        prompt_parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        )

    with track_model_call(model_name=model, task="select_best_image"):
        response = client.models.generate_content(
            model=model, contents=prompt_parts, config=config
        )
    return BestImage.model_validate_json(response.text)
