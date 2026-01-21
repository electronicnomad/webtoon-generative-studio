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

"""This module defines the default configuration for the Promptlandia application.

It uses a dataclass to define the configuration parameters, which are loaded
from environment variables. This allows for easy configuration of the
application without modifying the code.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass
class Default:
    """Default application configuration.

    This dataclass defines the default configuration for the application. The
    values are loaded from environment variables, with default values provided
    for some parameters.

    Attributes:
        PROJECT_ID: The Google Cloud project ID.
        LOCATION: The Google Cloud location to use for the generative AI model.
        MODEL_ID: The ID of the generative AI model to use.
        INIT_VERTEX: Whether to initialize the Vertex AI client.
    """

    PROJECT_ID: str = field(default_factory=lambda: os.environ.get("PROJECT_ID"))
    LOCATION: str = os.environ.get("LOCATION", "us-central1")
    MODEL_ID: str = os.environ.get("MODEL_ID", "gemini-2.5-flash")
    INIT_VERTEX: bool = True

    # Gemini Image Generation
    GEMINI_IMAGE_GEN_MODEL: str = os.environ.get(
        "GEMINI_IMAGE_GEN_MODEL", "gemini-2.5-flash-image",
    )
    GEMINI_IMAGE_GEN_LOCATION: str = os.environ.get(
        "GEMINI_IMAGE_GEN_LOCATION", "global",
    )
    GEMINI_IMAGE_GEN_API_BASE_URL: str = os.environ.get(
        "GEMINI_IMAGE_GEN_API_BASE_URL"
    )

    # Gemini Audio Analysis
    GEMINI_AUDIO_ANALYSIS_MODEL_ID: str = os.environ.get(
        "GEMINI_AUDIO_ANALYSIS_MODEL_ID", "gemini-2.5-flash",
    )

    # Collections
    GENMEDIA_FIREBASE_DB: str = os.environ.get("GENMEDIA_FIREBASE_DB", "(default)")
    GENMEDIA_COLLECTION_NAME: str = os.environ.get(
        "GENMEDIA_COLLECTION_NAME",
        "genmedia",
    )

    # Storage
    GENMEDIA_BUCKET: str = os.environ.get("GENMEDIA_BUCKET", f"{PROJECT_ID}-assets")
    VIDEO_BUCKET: str = os.environ.get("VIDEO_BUCKET", f"{PROJECT_ID}-assets/videos")
    IMAGE_BUCKET: str = os.environ.get("IMAGE_BUCKET", f"{PROJECT_ID}-assets/images")

    # Veo
    VEO_MODEL_ID: str = os.environ.get("VEO_MODEL_ID", "veo-2.0-generate-001")
    VEO_PROJECT_ID: str = os.environ.get("VEO_PROJECT_ID", PROJECT_ID)
    VEO_EXP_MODEL_ID: str = os.environ.get("VEO_EXP_MODEL_ID", "veo-2.0-generate-preview")
    VEO_EXP_PROJECT_ID: str = os.environ.get("VEO_EXP_PROJECT_ID", PROJECT_ID)

    # Character Consistency Temperatures
    TEMP_FORENSIC_ANALYSIS: float = 0.1
    TEMP_DESCRIPTION_TRANSLATION: float = 0.1
    TEMP_SCENE_GENERATION: float = 0.3
    TEMP_BEST_IMAGE_SELECTION: float = 0.2

    # Character Consistency Models
    CHARACTER_CONSISTENCY_IMAGEN_MODEL: str = "imagen-3.0-capability-001"
    CHARACTER_CONSISTENCY_VEO_MODEL: str = os.environ.get(
        "CHARACTER_CONSISTENCY_VEO_MODEL", "veo-2.0-generate-001"
    )
    CHARACTER_CONSISTENCY_GEMINI_MODEL: str = os.environ.get(
        "CHARACTER_CONSISTENCY_GEMINI_MODEL", MODEL_ID
    )

    # Imagen
    MODEL_IMAGEN2 = "imagegeneration@006"
    MODEL_IMAGEN = "imagen-3.0-generate-001"
    MODEL_IMAGEN_FAST = "imagen-3.0-fast-generate-001"
    MODEL_IMAGEN_EDITING = "imagen-3.0-capability-001"
    
    IMAGEN_GENERATED_SUBFOLDER: str = os.environ.get(
        "IMAGEN_GENERATED_SUBFOLDER", "generated_images"
    )
    IMAGEN_EDITED_SUBFOLDER: str = os.environ.get(
        "IMAGEN_EDITED_SUBFOLDER", "edited_images"
    )
