[English](#english) | [한국어](#korean)

<a id="english"></a>

# Application Environment Variables Explainer

This document details the environment variables used in the application, as defined in `config/default.py`. These variables control infrastructure settings, model versions, storage locations, and feature configurations.

> **Quick Start:** A `dotenv.template` file is provided in the root directory. To set up your local environment, copy this file to `.env` and populate the values:
>
> ```bash
> cp dotenv.template .env
> ```

## Core Infrastructure & Environment

These variables define the fundamental operating context of the application.

| Variable                    | Default                   | Description                                                                                                                            |
| :-------------------------- | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------- |
| **`PROJECT_ID`**            | _None_ (Required)         | The Google Cloud Project ID where resources (Vertex AI, Firestore, Storage) are located.                                               |
| **`LOCATION`**              | `us-central1`             | The default GCP region for most services (Vertex AI, etc.).                                                                            |
| **`APP_ENV`**               | `""` (Empty)              | Defines the environment (e.g., `dev`, `prod`). Used to load environment-specific content files like `config/about_content.{env}.json`. |
| **`API_BASE_URL`**          | `http://localhost:{PORT}` | The base URL for the application's backend APIs.                                                                                       |
| **`PORT`**                  | `8080`                    | The port the application server listens on.                                                                                            |
| **`SERVICE_ACCOUNT_EMAIL`** | _None_                    | The email of the service account used for authentication, if applicable.                                                               |
| **`GA_MEASUREMENT_ID`**     | _None_                    | Google Analytics Measurement ID for tracking user interactions.                                                                        |

## Gemini Models (Text & Multimodal)

Controls which versions of the Gemini models are used for various tasks.

| Variable                               | Default                  | Description                                                                            |
| :------------------------------------- | :----------------------- | :------------------------------------------------------------------------------------- |
| **`MODEL_ID`**                         | `gemini-2.5-flash`       | The primary Gemini model used for general text and reasoning tasks throughout the app. |
| **`GEMINI_IMAGE_GEN_MODEL`**           | `gemini-2.5-flash-image` | The specific model used for image generation features.                                 |
| **`GEMINI_IMAGE_GEN_LOCATION`**        | `global`                 | The region for the Gemini Image Generation API.                                        |
| **`GEMINI_AUDIO_ANALYSIS_MODEL_ID`**   | `gemini-2.5-flash`       | The model used specifically for analysis audio content.                                |
| **`GEMINI_WRITERS_WORKSHOP_MODEL_ID`** | `MODEL_ID`               | The model used for the Gemini Writers Workshop page. Defaults to `MODEL_ID`.           |

## Veo (Video Generation)

Configuration for the Veo video generation models.

| Variable                    | Default                     | Description                                               |
| :-------------------------- | :-------------------------- | :-------------------------------------------------------- |
| **`VEO_MODEL_ID`**          | `veo-2.0-generate-001`      | The standard Veo model version.                           |
| **`VEO_PROJECT_ID`**        | `PROJECT_ID`                | Allows using a different project for Veo quota if needed. |
| **`VEO_EXP_MODEL_ID`**      | `veo-3.0-generate-preview`  | The experimental/newer Veo model version.                 |
| **`VEO_EXP_FAST_MODEL_ID`** | `veo-3.0-fast-generate-001` | The faster, lower-latency experimental Veo model.         |
| **`VEO_EXP_PROJECT_ID`**    | `PROJECT_ID`                | Project ID for experimental Veo models.                   |

## Imagen (Image Generation & Editing)

Settings for Imagen models, including specialized versions for editing and product shots.

| Variable                             | Default                                  | Description                                                   |
| :----------------------------------- | :--------------------------------------- | :------------------------------------------------------------ |
| **`MODEL_IMAGEN_PRODUCT_RECONTEXT`** | `imagen-product-recontext-preview-06-30` | Model used for "Product Recontextualization" features.        |
| **`IMAGEN_GENERATED_SUBFOLDER`**     | `generated_images`                       | Subfolder in the GCS bucket where generated images are saved. |
| **`IMAGEN_EDITED_SUBFOLDER`**        | `edited_images`                          | Subfolder for images resulting from editing operations.       |

## Virtual Try-On (VTO)

Specific configuration for the Virtual Try-On feature.

| Variable                                   | Default                        | Description                                        |
| :----------------------------------------- | :----------------------------- | :------------------------------------------------- |
| **`VTO_LOCATION`**                         | `us-central1`                  | Region for the VTO API.                            |
| **`VTO_MODEL_ID`**                         | `virtual-try-on-preview-08-04` | The specific VTO model version.                    |
| **`GENMEDIA_VTO_MODEL_COLLECTION_NAME`**   | `genmedia-vto-model`           | Firestore collection for VTO model data.           |
| **`GENMEDIA_VTO_CATALOG_COLLECTION_NAME`** | `genmedia-vto-catalog`         | Firestore collection for VTO product catalog data. |

## Lyria (Music Generation)

Configuration for the Lyria music generation model.

| Variable                  | Default       | Description                            |
| :------------------------ | :------------ | :------------------------------------- |
| **`LYRIA_LOCATION`**      | `us-central1` | Region for Lyria API calls.            |
| **`LYRIA_MODEL_VERSION`** | `lyria-002`   | The version of the Lyria model to use. |
| **`LYRIA_PROJECT_ID`**    | `PROJECT_ID`  | Project ID for Lyria quota.            |

## Storage & Database (Firebase/GCS)

Defines where data and media assets are stored.

| Variable                       | Default                      | Description                                                    |
| :----------------------------- | :--------------------------- | :------------------------------------------------------------- |
| **`GENMEDIA_FIREBASE_DB`**     | `(default)`                  | The Firestore database ID.                                     |
| **`GENMEDIA_COLLECTION_NAME`** | `genmedia`                   | The main Firestore collection for storing generation metadata. |
| **`SESSIONS_COLLECTION_NAME`** | `sessions`                   | Firestore collection for user session data.                    |
| **`GENMEDIA_BUCKET`**          | `{PROJECT_ID}-assets`        | The primary GCS bucket for storing generated media.            |
| **`VIDEO_BUCKET`**             | `{PROJECT_ID}-assets/videos` | Specific bucket/path for video files.                          |
| **`IMAGE_BUCKET`**             | `{PROJECT_ID}-assets/images` | Specific bucket/path for image files.                          |
| **`MEDIA_BUCKET`**             | `{PROJECT_ID}-assets`        | Used by Lyria and potentially other legacy components.         |
| **`GCS_ASSETS_BUCKET`**        | _None_                       | Bucket for static assets used in the "About" page.             |

## Application Logic

| Variable                                 | Default                     | Description                                                        |
| :--------------------------------------- | :-------------------------- | :----------------------------------------------------------------- |
| **`LIBRARY_MEDIA_PER_PAGE`**             | `15`                        | Controls how many items appear per page in the media library.      |
| **`USE_MEDIA_PROXY`**                    | `true`                      | If `true`, media URLs are proxied to avoid CORS/hotlinking issues. |
| **`CHARACTER_CONSISTENCY_VEO_MODEL`**    | `veo-3.0-fast-generate-001` | Model used specifically in the Character Consistency workflow.     |
| **`CHARACTER_CONSISTENCY_GEMINI_MODEL`** | `MODEL_ID`                  | Gemini model used in the Character Consistency workflow.           |

## Terraform Configuration & Deployment

When deploying this application using Terraform (via `main.tf`), not all environment variables are exposed for configuration. The Terraform setup manages a specific subset of variables, primarily those related to infrastructure and core model IDs.

### 1. Variables Controllable via `variables.tf`

These variables are exposed in `variables.tf` and directly map to environment variables in the Cloud Run service. You can customize these by setting the corresponding Terraform variable during deployment.

| Terraform Variable    | Maps to App Env Var   | Default in Terraform       |
| :-------------------- | :-------------------- | :------------------------- |
| `project_id`          | `PROJECT_ID`          | _(Required)_               |
| `region`              | `LOCATION`            | `us-central1`              |
| `model_id`            | `MODEL_ID`            | `gemini-2.5-flash`         |
| `veo_model_id`        | `VEO_MODEL_ID`        | `veo-3.0-generate-001`     |
| `veo_exp_model_id`    | `VEO_EXP_MODEL_ID`    | `veo-3.0-generate-preview` |
| `lyria_model_id`      | `LYRIA_MODEL_VERSION` | `lyria-002`                |
| `edit_images_enabled` | `EDIT_IMAGES_ENABLED` | `true`                     |

### 2. Variables Automatically Managed by Terraform

These variables are computed within `main.tf` based on the resources Terraform creates (e.g., bucket names, service account emails). You generally **cannot** change these via `variables.tf` as they ensure the application correctly connects to the provisioned infrastructure.

| App Env Var             | Source in `main.tf`       | Value Logic                             |
| :---------------------- | :------------------------ | :-------------------------------------- |
| `GENMEDIA_BUCKET`       | `local.asset_bucket_name` | `creative-studio-{project_id}-assets`   |
| `VIDEO_BUCKET`          | `local.asset_bucket_name` | Same as above                           |
| `MEDIA_BUCKET`          | `local.asset_bucket_name` | Same as above                           |
| `IMAGE_BUCKET`          | `local.asset_bucket_name` | Same as above                           |
| `GCS_ASSETS_BUCKET`     | `local.asset_bucket_name` | Same as above                           |
| `GENMEDIA_FIREBASE_DB`  | Resource Attribute        | Name of the created Firestore DB        |
| `SERVICE_ACCOUNT_EMAIL` | Resource Attribute        | Email of the created Service Account    |
| `LYRIA_PROJECT_ID`      | `var.project_id`          | Forces Lyria to use the main project ID |

### 3. Variables NOT Set by Terraform (Using Python Defaults)

The following variables are **not** explicitly set in the `main.tf` configuration. This means the application will use the **default values defined in `config/default.py`** when deployed via Terraform.

- **Gemini Models:** `GEMINI_IMAGE_GEN_MODEL`, `GEMINI_IMAGE_GEN_LOCATION`, `GEMINI_AUDIO_ANALYSIS_MODEL_ID`
- **Veo:** `VEO_PROJECT_ID`, `VEO_EXP_FAST_MODEL_ID`, `VEO_EXP_PROJECT_ID`
- **VTO (Virtual Try-On):** `VTO_LOCATION`, `VTO_MODEL_ID`, `GENMEDIA_VTO_*` collection names.
- **Imagen:** `MODEL_IMAGEN_PRODUCT_RECONTEXT`, `IMAGEN_GENERATED_SUBFOLDER`, `IMAGEN_EDITED_SUBFOLDER`
- **App Logic:** `APP_ENV`, `API_BASE_URL`, `GA_MEASUREMENT_ID`, `LIBRARY_MEDIA_PER_PAGE`, `USE_MEDIA_PROXY`
- **Collections:** `GENMEDIA_COLLECTION_NAME`, `SESSIONS_COLLECTION_NAME`

### How to Deploy with Custom Values

To change a variable from **Group 3** (e.g., `GEMINI_IMAGE_GEN_MODEL`) when deploying with Terraform:

1.  **Modify `variables.tf`:** Add a new variable definition.
    ```hcl
    variable "gemini_image_model" {
      description = "Model ID for Gemini Image Generation"
      type        = string
      default     = "gemini-3-pro-image-preview"
    }
    ```
2.  **Modify `main.tf`:** Update the `locals` block to include the new environment variable mapping.
    ```hcl
    locals {
      webtoon_studio_env_vars = {
        # ... existing vars ...
        GEMINI_IMAGE_GEN_MODEL = var.gemini_image_model
      }
    }
    ```

---

<a id="korean"></a>

# 애플리케이션 환경 변수 설명 (Application Environment Variables Explainer)

이 문서는 `config/default.py`에 정의된 애플리케이션에서 사용되는 환경 변수에 대해 자세히 설명합니다. 이 변수들은 인프라 설정, 모델 버전, 저장 위치 및 기능 구성을 제어합니다.

> **빠른 시작:** 루트 디렉토리에서 `dotenv.template` 파일이 제공됩니다. 로컬 환경을 설정하려면 이 파일을 `.env`로 복사하고 값을 입력하세요:
>
> ```bash
> cp dotenv.template .env
> ```

## 핵심 인프라 및 환경 (Core Infrastructure & Environment)

이 변수들은 애플리케이션의 기본적인 운영 컨텍스트를 정의합니다.

| 변수                        | 기본값                    | 설명                                                                                                                        |
| :-------------------------- | :------------------------ | :-------------------------------------------------------------------------------------------------------------------------- |
| **`PROJECT_ID`**            | _없음_ (필수)             | 리소스(Vertex AI, Firestore, Storage)가 위치한 Google Cloud 프로젝트 ID입니다.                                              |
| **`LOCATION`**              | `us-central1`             | 대부분의 서비스(Vertex AI 등)에 대한 기본 GCP 리전입니다.                                                                   |
| **`APP_ENV`**               | `""` (비어 있음)          | 환경(예: `dev`, `prod`)을 정의합니다. `config/about_content.{env}.json`과 같은 환경별 콘텐츠 파일을 로드하는 데 사용됩니다. |
| **`API_BASE_URL`**          | `http://localhost:{PORT}` | 애플리케이션의 백엔드 API에 대한 기본 URL입니다.                                                                            |
| **`PORT`**                  | `8080`                    | 애플리케이션 서버가 수신 대기하는 포트입니다.                                                                               |
| **`SERVICE_ACCOUNT_EMAIL`** | _없음_                    | 인증에 사용되는 서비스 계정의 이메일입니다(해당되는 경우).                                                                  |
| **`GA_MEASUREMENT_ID`**     | _없음_                    | 사용자 상호 작용을 추적하기 위한 Google Analytics 측정 ID입니다.                                                            |

## Gemini 모델 (텍스트 및 멀티모달)

다양한 작업에 사용되는 Gemini 모델의 버전을 제어합니다.

| 변수                                   | 기본값                   | 설명                                                                               |
| :------------------------------------- | :----------------------- | :--------------------------------------------------------------------------------- |
| **`MODEL_ID`**                         | `gemini-2.5-flash`       | 앱 전체에서 일반적인 텍스트 및 추론 작업에 사용되는 기본 Gemini 모델입니다.        |
| **`GEMINI_IMAGE_GEN_MODEL`**           | `gemini-2.5-flash-image` | 이미지 생성 기능에 사용되는 특정 모델입니다.                                       |
| **`GEMINI_IMAGE_GEN_LOCATION`**        | `global`                 | Gemini 이미지 생성 API의 리전입니다.                                               |
| **`GEMINI_AUDIO_ANALYSIS_MODEL_ID`**   | `gemini-2.5-flash`       | 오디오 콘텐츠 분석에 특별히 사용되는 모델입니다.                                   |
| **`GEMINI_WRITERS_WORKSHOP_MODEL_ID`** | `MODEL_ID`               | Gemini Writers Workshop 페이지에서 사용되는 모델입니다. 기본값은 `MODEL_ID`입니다. |

## Veo (비디오 생성)

Veo 비디오 생성 모델에 대한 구성입니다.

| 변수                        | 기본값                      | 설명                                                       |
| :-------------------------- | :-------------------------- | :--------------------------------------------------------- |
| **`VEO_MODEL_ID`**          | `veo-2.0-generate-001`      | 표준 Veo 모델 버전입니다.                                  |
| **`VEO_PROJECT_ID`**        | `PROJECT_ID`                | 필요한 경우 Veo 쿼터에 다른 프로젝트를 사용할 수 있습니다. |
| **`VEO_EXP_MODEL_ID`**      | `veo-3.0-generate-preview`  | 실험적/최신 Veo 모델 버전입니다.                           |
| **`VEO_EXP_FAST_MODEL_ID`** | `veo-3.0-fast-generate-001` | 더 빠르고 지연 시간이 짧은 실험적 Veo 모델입니다.          |
| **`VEO_EXP_PROJECT_ID`**    | `PROJECT_ID`                | 실험적 Veo 모델에 대한 프로젝트 ID입니다.                  |

## Imagen (이미지 생성 및 편집)

이미지 편집 및 제품 샷을 위한 특수 버전을 포함한 Imagen 모델 설정입니다.

| 변수                                 | 기본값                                   | 설명                                                                     |
| :----------------------------------- | :--------------------------------------- | :----------------------------------------------------------------------- |
| **`MODEL_IMAGEN_PRODUCT_RECONTEXT`** | `imagen-product-recontext-preview-06-30` | "제품 재맥락화(Product Recontextualization)" 기능에 사용되는 모델입니다. |
| **`IMAGEN_GENERATED_SUBFOLDER`**     | `generated_images`                       | 생성된 이미지가 저장되는 GCS 버킷의 하위 폴더입니다.                     |
| **`IMAGEN_EDITED_SUBFOLDER`**        | `edited_images`                          | 편집 작업 결과 이미지를 위한 하위 폴더입니다.                            |

## 가상 착용 (Virtual Try-On, VTO)

가상 착용 기능에 대한 구체적인 구성입니다.

| 변수                                       | 기본값                         | 설명                                                    |
| :----------------------------------------- | :----------------------------- | :------------------------------------------------------ |
| **`VTO_LOCATION`**                         | `us-central1`                  | VTO API를 위한 리전입니다.                              |
| **`VTO_MODEL_ID`**                         | `virtual-try-on-preview-08-04` | 특정 VTO 모델 버전입니다.                               |
| **`GENMEDIA_VTO_MODEL_COLLECTION_NAME`**   | `genmedia-vto-model`           | VTO 모델 데이터를 위한 Firestore 컬렉션입니다.          |
| **`GENMEDIA_VTO_CATALOG_COLLECTION_NAME`** | `genmedia-vto-catalog`         | VTO 제품 카탈로그 데이터를 위한 Firestore 컬렉션입니다. |

## Lyria (음악 생성)

Lyria 음악 생성 모델에 대한 구성입니다.

| 변수                      | 기본값        | 설명                                 |
| :------------------------ | :------------ | :----------------------------------- |
| **`LYRIA_LOCATION`**      | `us-central1` | Lyria API 호출을 위한 리전입니다.    |
| **`LYRIA_MODEL_VERSION`** | `lyria-002`   | 사용할 Lyria 모델의 버전입니다.      |
| **`LYRIA_PROJECT_ID`**    | `PROJECT_ID`  | Lyria 쿼터에 대한 프로젝트 ID입니다. |

## 스토리지 및 데이터베이스 (Firebase/GCS)

데이터 및 미디어 자산이 저장되는 위치를 정의합니다.

| 변수                           | 기본값                       | 설명                                                         |
| :----------------------------- | :--------------------------- | :----------------------------------------------------------- |
| **`GENMEDIA_FIREBASE_DB`**     | `(default)`                  | Firestore 데이터베이스 ID입니다.                             |
| **`GENMEDIA_COLLECTION_NAME`** | `genmedia`                   | 생성 메타데이터를 저장하기 위한 메인 Firestore 컬렉션입니다. |
| **`SESSIONS_COLLECTION_NAME`** | `sessions`                   | 사용자 세션 데이터를 위한 Firestore 컬렉션입니다.            |
| **`GENMEDIA_BUCKET`**          | `{PROJECT_ID}-assets`        | 생성된 미디어를 저장하기 위한 기본 GCS 버킷입니다.           |
| **`VIDEO_BUCKET`**             | `{PROJECT_ID}-assets/videos` | 비디오 파일을 위한 특정 버킷/경로입니다.                     |
| **`IMAGE_BUCKET`**             | `{PROJECT_ID}-assets/images` | 이미지 파일을 위한 특정 버킷/경로입니다.                     |
| **`MEDIA_BUCKET`**             | `{PROJECT_ID}-assets`        | Lyria 및 잠재적으로 다른 레거시 구성 요소에서 사용됩니다.    |
| **`GCS_ASSETS_BUCKET`**        | _없음_                       | "About" 페이지에서 사용되는 정적 자산을 위한 버킷입니다.     |

## 애플리케이션 로직 (Application Logic)

| 변수                                     | 기본값                      | 설명                                                                       |
| :--------------------------------------- | :-------------------------- | :------------------------------------------------------------------------- |
| **`LIBRARY_MEDIA_PER_PAGE`**             | `15`                        | 미디어 라이브러리의 페이지당 표시되는 아이템 수를 제어합니다.              |
| **`USE_MEDIA_PROXY`**                    | `true`                      | `true`인 경우, CORS/핫링크 문제를 방지하기 위해 미디어 URL이 프록시됩니다. |
| **`CHARACTER_CONSISTENCY_VEO_MODEL`**    | `veo-3.0-fast-generate-001` | 캐릭터 일관성 워크플로에서 특별히 사용되는 모델입니다.                     |
| **`CHARACTER_CONSISTENCY_GEMINI_MODEL`** | `MODEL_ID`                  | 캐릭터 일관성 워크플로에서 사용되는 Gemini 모델입니다.                     |

## Terraform 구성 및 배포

Terraform을 사용하여 이 애플리케이션을 배포할 때(`main.tf`를 통해), 모든 환경 변수가 구성을 위해 노출되는 것은 아닙니다. Terraform 설정은 주로 인프라 및 핵심 모델 ID와 관련된 특정 변수 하위 집합을 관리합니다.

### 1. `variables.tf`를 통해 제어 가능한 변수

이 변수들은 `variables.tf`에 노출되어 있으며 Cloud Run 서비스의 환경 변수에 직접 매핑됩니다. 배포 중에 해당 Terraform 변수를 설정하여 사용자 정의할 수 있습니다.

| Terraform 변수        | 앱 환경 변수에 매핑   | Terraform 기본값           |
| :-------------------- | :-------------------- | :------------------------- |
| `project_id`          | `PROJECT_ID`          | _(필수)_                   |
| `region`              | `LOCATION`            | `us-central1`              |
| `model_id`            | `MODEL_ID`            | `gemini-2.5-flash`         |
| `veo_model_id`        | `VEO_MODEL_ID`        | `veo-3.0-generate-001`     |
| `veo_exp_model_id`    | `VEO_EXP_MODEL_ID`    | `veo-3.0-generate-preview` |
| `lyria_model_id`      | `LYRIA_MODEL_VERSION` | `lyria-002`                |
| `edit_images_enabled` | `EDIT_IMAGES_ENABLED` | `true`                     |

### 2. Terraform에 의해 자동으로 관리되는 변수

이 변수들은 Terraform이 생성하는 리소스(예: 버킷 이름, 서비스 계정 이메일)를 기반으로 `main.tf` 내에서 계산됩니다. 애플리케이션이 프로비저닝된 인프라에 올바르게 연결되도록 보장하므로 일반적으로 `variables.tf`를 통해 변경할 수 **없습니다**.

| 앱 환경 변수            | `main.tf`에서의 소스      | 값 로직                                      |
| :---------------------- | :------------------------ | :------------------------------------------- |
| `GENMEDIA_BUCKET`       | `local.asset_bucket_name` | `creative-studio-{project_id}-assets`        |
| `VIDEO_BUCKET`          | `local.asset_bucket_name` | 위와 동일                                    |
| `MEDIA_BUCKET`          | `local.asset_bucket_name` | 위와 동일                                    |
| `IMAGE_BUCKET`          | `local.asset_bucket_name` | 위와 동일                                    |
| `GCS_ASSETS_BUCKET`     | `local.asset_bucket_name` | 위와 동일                                    |
| `GENMEDIA_FIREBASE_DB`  | 리소스 속성               | 생성된 Firestore DB의 이름                   |
| `SERVICE_ACCOUNT_EMAIL` | 리소스 속성               | 생성된 서비스 계정의 이메일                  |
| `LYRIA_PROJECT_ID`      | `var.project_id`          | Lyria가 메인 프로젝트 ID를 사용하도록 강제함 |

### 3. Terraform에 의해 설정되지 않는 변수 (Python 기본값 사용)

다음 변수들은 `main.tf` 구성에 명시적으로 설정되지 **않습니다**. 즉, Terraform을 통해 배포할 때 애플리케이션은 **`config/default.py`에 정의된 기본값**을 사용합니다.

- **Gemini Models:** `GEMINI_IMAGE_GEN_MODEL`, `GEMINI_IMAGE_GEN_LOCATION`, `GEMINI_AUDIO_ANALYSIS_MODEL_ID`
- **Veo:** `VEO_PROJECT_ID`, `VEO_EXP_FAST_MODEL_ID`, `VEO_EXP_PROJECT_ID`
- **VTO (Virtual Try-On):** `VTO_LOCATION`, `VTO_MODEL_ID`, `GENMEDIA_VTO_*` 컬렉션 이름.
- **Imagen:** `MODEL_IMAGEN_PRODUCT_RECONTEXT`, `IMAGEN_GENERATED_SUBFOLDER`, `IMAGEN_EDITED_SUBFOLDER`
- **앱 로직:** `APP_ENV`, `API_BASE_URL`, `GA_MEASUREMENT_ID`, `LIBRARY_MEDIA_PER_PAGE`, `USE_MEDIA_PROXY`
- **컬렉션:** `GENMEDIA_COLLECTION_NAME`, `SESSIONS_COLLECTION_NAME`

### 사용자 지정 값으로 배포하는 방법

Terraform으로 배포할 때 **그룹 3**의 변수(예: `GEMINI_IMAGE_GEN_MODEL`)를 변경하려면:

1.  **`variables.tf` 수정:** 새 변수 정의를 추가합니다.
    ```hcl
    variable "gemini_image_model" {
      description = "Gemini 이미지 생성을 위한 모델 ID"
      type        = string
      default     = "gemini-3-pro-image-preview"
    }
    ```
2.  **`main.tf` 수정:** 새 환경 변수 매핑을 포함하도록 `locals` 블록을 업데이트합니다.
    ```hcl
    locals {
      webtoon_studio_env_vars = {
        # ... 기존 변수 ...
        GEMINI_IMAGE_GEN_MODEL = var.gemini_image_model
      }
    }
    ```
