[English](#english) | [한국어](#korean)

<a id="english"></a>

# Gnomeregan Binary Studio

A customized fork of Vertex AI Creative Studio https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio

> ###### _This is not an officially supported Google product. This project is not eligible for the [Google Open Source Software Vulnerability Rewards Program](https://bughunters.google.com/open-source-security). This project is intended for demonstration purposes only. It is not intended for use in a production environment._

![GenMedia Creative Studio v.next](https://github.com/user-attachments/assets/da5ad223-aa6e-413c-b36e-5d63e5d5b758)

![GenMedia Creative Studio v.next](https://github.com/user-attachments/assets/61977f3c-dbb6-4002-b8c0-77d57aa03cce)

## Table of Contents

- [GenMedia Creative Studio | Vertex AI](#genmedia-creative-studio--vertex-ai)
- [Table of Contents](#table-of-contents)
- [GenMedia Creative Studio](#genmedia-creative-studio)
  - [Experiments](#experiments)
- [Deploying GenMedia Creative Studio](#deploying-genmedia-creative-studio)
  - [Prerequisites](#prerequisites)
    - [1. Download the source code for this project](#1-download-the-source-code-for-this-project)
    - [2. Export Environment Variables](#2-export-environment-variables)
  - [Deploying with Custom Domain](#deploying-with-custom-domain)
    - [1. Initialize Terraform](#1-initialize-terraform)
    - [2. Create a DNS A record for the domain name](#2-create-a-dns-a-record-for-the-domain-name)
    - [3. Build and Deploy Container Image](#3-build-and-deploy-container-image)
    - [4. Wait for certificate to go to provisioned state](#4-wait-for-certificate-to-go-to-provisioned-state)
  - [Deploying using Cloud Run Domain](#deploying-using-cloud-run-domain)
    - [1. Initialize Terraform](#1-initialize-terraform-1)
    - [2. Build and Deploy Container Image](#2-build-and-deploy-container-image)
    - [3. Edit Cloud Run's IAP Policy to provide initial user's access](#3-edit-cloud-runs-iap-policy-to-provide-initial-users-access)
  - [Deploying to Cloud Shell for Testing](#deploying-to-cloud-shell-for-testing)
- [Adding Additional Users](#adding-additional-users)
- [Solution Design](#solution-design)
  - [Custom Domain Using Identity Aware Proxy w/Load Balancer](#custom-domain-using-identity-aware-proxy-wload-balancer)
  - [Cloud Run Domain Using Identity Aware Proxy w/Cloud Run](#cloud-run-domain-using-identity-aware-proxy-wcloud-run)
  - [Solution Components](#solution-components)
    - [Runtime Components](#runtime-components)
    - [Build time Components](#build-time-components)
  - [Setting up your development environment](#setting-up-your-development-environment)
    - [Python virtual environment](#python-virtual-environment)
    - [Application Environment variables](#application-environment-variables)
  - [GenMedia Creative Studio - Developing](#genmedia-creative-studio---developing)
    - [Running](#running)
    - [Developing](#developing)
  - [Contributing changes](#contributing-changes)
  - [Licensing](#licensing)
- [Disclaimer](#disclaimer)

## GenMedia Creative Studio

> **Browser Compatibility:** For the best experience, we recommend using Google Chrome. Some features may not work as expected on other browsers, such as Safari or Firefox.

GenMedia Creative Studio is a web application showcasing Google Cloud's generative media - Veo, Lyria, Chirp, Gemini 2.5 Flash Image Generation (nano-banana), and Gemini TTS along with custom workflows and techniques for creative exploration and inspiration. We're looking forward to see what you create!

Current featureset

- Image: Imagen 3, Imagen 4, Virtual Try-On, Gemini 2.5 Flash Image Generation
- Video: Veo 2, Veo 3
- Music: Lyria
- Speech: Chirp 3 HD, Gemini Text to Speech
- Workflows: Character Consistency, Shop the Look, Starter Pack Moodboard, Interior Designer, Cartoon Pro
- Asset Library

This is built using [Mesop](https://mesop-dev.github.io/mesop/), an open source Python framework used at Google for rapid AI app development, and the [scaffold for Studio style apps](https://github.com/ghchinoy/studio-scaffold).

## Experiments

The [Experimental folder](./experiments/) contains a variety of stand-alone applications and new and upcoming features that showcase cutting-edge capabilities with generative AI.

Here's a glimpse of what you'll find:

**MCP Tools**

- **MCP Tools for Genmedia:** Model Context Protocol servers for Veo, Imagen, Lyria, Chirp, and Gemini to bring creativity to your agents.

**Combined Workflows**

- **Countdown Workflow:** An automated two-stage pipeline to create branded countdown videos.
- **Storycraft:** An AI-powered video storyboard generation platform that transforms text descriptions into complete video narratives.
  - **Creative GenMedia Workflow:** An end-to-end workflow to produce high-quality, on-brand creative media.
  - **Run, Veo, Run:** A real-time, multimodal video generation experiment that creates a branching narrative loop using Veo 3.1 for video extension and Gemini 3 for context awareness.

**Prompting Techniques**

- **Promptlandia:** A powerful web app to analyze, refine, and improve your prompts.
- **Veo Genetic Prompt Optimizer:** An automated system to evolve and refine high-level "metaprompts" for Veo.
- **Character & Item Consistency:** Workflows for maintaining consistency for characters and items across video scenes.

**Image Generation & Analysis**

- **Virtual Try-On:** A notebook for virtually trying on outfits at scale.
- **Imagen Product Recontextualization:** Tools for large-scale product image recontextualization.
- **Arena:** A visual arena for rating and comparing images from different models.

**Audio & Video**

- **Creative Podcast Assistant:** A notebook for creating a podcast with generative media.
- **Babel:** An experimental app for Chirp 3 HD voices.

...and much more! For a full, detailed list of all experiments, please see the [Experiments README](./experiments/README.md).

## 🤖 AI Assistants

This repository uses **Google's Gemini CLI** to automate software engineering tasks.

- **Code Reviewer:** Automatically reviews Pull Requests for bugs and security issues.
- **Issue Triage:** Automatically labels and categorizes new issues.
- **Maintainer Commands:** Allows maintainers to manually trigger reviews (`@gemini-cli /review`) or ask questions (`@gemini-cli Explain this...`).

For detailed documentation on the agents and workflows, see [AGENTS.md](./AGENTS.md).

## Deploying GenMedia Creative Studio

Deployment of GenMedia Creative Studio is accomplished using a combination of Terraform and Cloud Build. Terraform is used to deploy the infrastructure and Cloud Build is used to create the container image and update the Cloud Run service to use it.

You have two deployment options for this application:

1. [Deploy using a custom domain](#deploying-with-custom-domain). Use this if:
   - You need to support external identities. Included Terraform script does not support this; however, you can customize the script.
   - You prefer more control over the domain used
2. [Deploy using the autogenerated Cloud Run Domain](#deploying-using-cloud-run-domain). Use this if:
   - You can not create a DNS entry
   - [IAP for Cloud Run Known Limitations](https://cloud.google.com/iap/docs/enabling-cloud-run#known_limitations) are non-blockers (e.g., no external identities, no Cloud CDN support)

Choose one of the two methods to proceed.

### Prerequisites

You'll need the following

- An existing Google Cloud Project
- If you want to use a custom domain, you need the ability to create a DNS A record for your target domain that resolves to the provisioned load balancer

#### 1. Download the source code for this project

Download the source

```bash
git clone https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio.git
```

#### 2. Export Environment Variables

The following environment variables are the minimum required to deploy the application.

- REGION - Should be set to `us-central1`. Prior to selecting a different region, validate the GenAI models needed are available [here](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#google_model_endpoint_locations).
- PROJECT_ID - Set to the desired Google Cloud project's ID, obtained via `gcloud` below or you can enter it manually.
- DOMAIN_NAME - Update with the DNS name to be used to reach the web application (e.g., creativestudio.example.com). A Google Cloud Managed certificate will be created for this domain.
- INITIAL_USERS - List of email addresses of initial users given access to the web application (e.g., '["admin@example.com", "user@example.com"]')

Replace the example values and execute the script below:

```bash
export REGION=us-central1 
export PROJECT_ID=$(gcloud config get project) 
export INITIAL_USERS='["admin@example.com"]'
```

## Deploying with Custom Domain

Follow these steps if you are going to deploy GenMedia Creative Studio using your own custom domain. You will need the ability to create a DNS A record if you choose this deployment option.

### 1. Initialize Terraform

Because you are using a custom domain, you will need to export one more variable with the DNS name for the domain that will be used to navigate to GenMedia Creative Studio.

```bash
export DOMAIN_NAME=creativestudio.example.com
```

Make sure your command line is in the folder containing this README (i.e., in the root of the main repository, /). Then create the `terraform.tfvars` using the following command:

```bash
cat > terraform.tfvars << EOF
project_id = "$PROJECT_ID"
initial_users = $INITIAL_USERS
domain = "$DOMAIN_NAME"
EOF

terraform init
terraform apply
```

### 2. Create a DNS A record for the domain name

A load balancer and a Google Cloud managed certificate are provisioned by the Terraform configuration file. You must create a DNS A record that resolves to the IP address of the provisioned load balancer. Below is a sample output from running the `terraform apply` command, showing where the provisioned application balancer's IP is displayed.

![Load Balancer IP Address](https://github.com/user-attachments/assets/e9d6af9a-9445-441d-b89a-04b412f9baac)

> **Note:** If `load-balancer-ip = ""` appears in the `terraform apply` outputs, ensure `use_lb = true` is set in your `terraform.tfvars` file and run `terraform apply` again.

If you use Google Cloud DNS, follow the steps [here](https://cloud.google.com/dns/docs/records). Provisioning a Google-managed certificate might take up to 60 minutes from the moment your DNS and load balancer configuration changes have propagated across the internet.

> If you take too long to create the A record, usually >15 minutes or the DNS entry resolves to any other IP address than the load balancer's, provisioning of the Google Cloud Managed certificate may fail with a status of `FAILED_NOT_VISIBLE`. If this is the case, make sure the DNS A record is updated correctly and follow the steps [here](https://cloud.google.com/load-balancing/docs/ssl-certificates/troubleshooting?#verify_configuration_changes).

### 3. Build and Deploy Container Image

A shell script, `build.sh`, is included in this repo that submits a build to Cloud Build which builds and deploys the application's container image. Use the following command:

```bash
./build.sh
```

### 4. Wait for certificate to go to provisioned state

With both the infrastructure and application deployed, you are just waiting for the certificate to complete provisioning. Once you see the status as "ACTIVE" and the "In use by" section populated (see sample below), your application is ready for use. You can navigate to the [Certificate Manager GCP Console page](https://console.cloud.google.com/security/ccm/list/lbCertificates), and select the certificate to keep an eye on the status.

![Provisioned Certificate](https://github.com/user-attachments/assets/20c0fb6b-c865-40e1-a9cc-fc3b0d349184)

## Deploying using Cloud Run Domain

If you are unable to create a DNS record in your corporate domain, you can also use the autogenerated Cloud Run domain along with it's preview support for IAP to secure the endpoint.

> Currently, Cloud Run's integration with IAP is a preview feature and is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the [Service Specific Terms](https://cloud.google.com/terms/service-terms#1). Pre-GA features are available "as is" and might have limited support. For more information, see the [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

### 1. Initialize Terraform

Make sure your command line is in the folder containing this README (i.e., in the root of the main repository, /). Then create the `terraform.tfvars` using the following command:

```bash
cat > terraform.tfvars << EOF
project_id = "$PROJECT_ID"
initial_users = $INITIAL_USERS
use_lb = false
EOF

terraform init
terraform apply
```

Make sure to take note of the Cloud Run URL that is output. This is what you will navigate to in your browser to access the application. Before doing that though, you need to build and deploy the container image.

![Cloud Run URL output](https://github.com/user-attachments/assets/e8729bfb-151b-4cbc-9006-6f76f5ce713e)

### 2. Build and Deploy Container Image

A shell script, `build.sh`, is included in this repo that submits a build to Cloud Build which builds and deploys the application's container image. Use the following command:

```bash
./build.sh
```

### 3. Edit Cloud Run's IAP Policy to provide initial user's access

The last step is to change the IAP policy of the Cloud Run service to provide access to a user. You can also use a group but for the purposes of this example, a single user is given access.

```bash
gcloud beta iap web add-iam-policy-binding \
--project=$PROJECT_ID \
--region=$REGION \
--member=user:$INITIAL_USER \
--role=roles/iap.httpsResourceAccessor \
--resource-type=cloud-run \
--service=creative-studio
```

Congratulations, you can now navigate to the address provided in the `cloud-run-app-url` Terraform output.

## Deploying to Cloud Shell for Testing

Use this option if you want to quickly run the UI without having to setup a local development environment. To get started, use Cloud Shell and follow the tutorial instructions.

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio.git&cloudshell_tutorial=TUTORIAL.md)

# Updating GenMedia Creative Studio

As new features and fixes are added to GenMedia Creative Studio, you will want to update your deployment. You do **not** need to destroy your existing infrastructure.

## Updating Application Code

If you only need to update the application code (Python files, UI changes):

1. Pull the latest changes from the repository:

   ```bash
   git pull
   ```

2. Run the build script:

   ```bash
   ./build.sh
   ```

This script submits a new build to Cloud Build, creates a new container image, and updates the existing Cloud Run service.

## Updating Infrastructure

If the updates include changes to the Terraform configuration (e.g., new environment variables, new Google Cloud services):

1. Pull the latest changes:

   ```bash
   git pull
   ```

2. Initialize Terraform to download any new provider requirements:

   ```bash
   terraform init -upgrade
   ```

3. Apply the changes. Terraform will only update what has changed:

   ```bash
   terraform apply
   ```

# Adding Additional Users

With any of the deployment options above that use IAP, if you need to add additional users, there are two steps to take to make sure those users can both access the application and the images generated:

- Application Access - Add the user to IAP. Follow [these steps](https://cloud.google.com/iap/docs/managing-access#managing_access_console) if you deployed using a load balancer, granting the user the _IAP-Secured Web App User_ role. If you deployed using only the Cloud Run provided URL, follow [these steps](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run#manage_user_or_group_access).
- Image Access - The images are served using the authenticated GCS URL of each storage object so users need to be granted the _Storage Object Viewer_ role. The name of the bucket is available as the `assets-bucket` Terraform output.

> **Note:** For the application to function correctly, the **Cloud Run service account** must have the **`Storage Object Viewer`** (`roles/storage.objectViewer`) role on the GCS bucket. This allows the application to read media assets and serve them to users through the proxy.

For detailed instructions on adding internal vs. external users and troubleshooting access issues, please refer to the [User Management Guide](USER_MANAGEMENT.md).

# Frequently Asked Questions

For common questions and troubleshooting tips, please refer to the [FAQ](FAQ.md).

# Solution Design

There are two way to deploy this solution. One using a custom domain with a load balancer and IAP integration. The other is using Cloud Run's default URL and integrating IAP with Cloud Run. The below diagrams depict the components used for each option.

## Custom Domain Using Identity Aware Proxy w/Load Balancer

![Solution Design - LB IAP](https://github.com/user-attachments/assets/ad057afb-4d7c-4857-b074-427eccbfaaa0)

## Cloud Run Domain Using Identity Aware Proxy w/Cloud Run

![Solution Design - Cloud Run IAP](https://github.com/user-attachments/assets/ec2c1e04-6890-4246-b134-9923955c0486)

The above diagram depicts the components that make up the Creative Studio solution. Items of note:

- DNS entry _is not_ deployed as part of the provided Terraform configuration files. You will need to create a DNS A record that resolves to the IP address of the provisioned load balancer so that certificate provisioning succeeds.
- Users are authenticated with Google Accounts and access is [managed through Identity Aware Proxy (IAP)](https://cloud.google.com/iap/docs/managing-access). IAP does support external identities and you can learn more [here](https://cloud.google.com/iap/docs/enable-external-identities).

## Solution Components

### Runtime Components

- [Load Balancer](https://cloud.google.com/load-balancing) - Provides the HTTP access to the Cloud Run hosted application

- [Identity Aware Proxy](https://cloud.google.com/security/products/iap) - Limits access to web application for only authenticated users or groups
- [Cloud Run](https://cloud.google.com/run) - Serverless container runtime used to host Mesop application
- [Cloud Firestore](https://firebase.google.com/docs/firestore) - Data store for the image / video / audio metadata. If you're new to Firebase, a great starting point is [here](https://firebase.google.com/docs/projects/learn-more#firebase-cloud-relationship).
- [Cloud Storage](https://cloud.google.com/storage) - A bucket is used to store the image / video / audio files

### Build time Components

- [Cloud Build](https://cloud.google.com/build) - Uses build packs to create the container images, push them to Artifact Registry and update the Cloud Run service to use the latest image version. To simplify deployment, connections to a GitHub project and triggers are not deployed w/Terraform. The source code that was cloned locally is compressed and pushed to Cloud Storage. It is this snapshot of the source that is used to build the container image.

- [Artifact Registry](https://cloud.google.com/artifact-registry/docs/overview) - Used to store the container images for the web aplication
- [Cloud Storage](https://cloud.google.com/storage) - A bucket is used to store a compressed file of the source used for the build

## Setting up your development environment

### Python virtual environment

A python virtual environment, with required packages installed.

Using the [uv](https://github.com/astral-sh/uv) virtual environment and package manager:

```
# sync the requirements to a virtual environment
uv sync
```

If you've done this before, you can also use the command `uv sync --upgrade` to check for any package version upgrades.

### Application Environment variables

Use the included dotenv.template and create a `.env` file with your specific environment variables.

Only one environment variable is required:

- `PROJECT_ID` your Google Cloud Project ID, obtained via `gcloud config get project`

See the template dotenv.template file for the defaults and what environment variable options are available.

## GenMedia Creative Studio - Developing

### Running

Once you have your environment variables set, either on the command line or an in .env file:

```bash
uv run main.py
```

### Developing

Please see the [Developer's Guide](./DEVELOPERS_GUIDE.md) for more information on how this application was built, including specific information about [Mesop](https://mesop-dev.github.io/mesop/) and the [scaffold for Studio style apps](https://github.com/ghchinoy/studio-scaffold).

When developing this app, since it's a FastAPI application that serves Mesop, please use the following

```bash
uv run main.py
```

Traditional Mesop hot reload capabilities (i.e. `mesop main.py`) are not fully available at this time.

## Contributing changes

Interested in contributing? Please open an issue describing the intended change. Additionally, bug fixes are welcome, either as pull requests or as GitHub issues.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.

## Licensing

Code in this repository is licensed under the Apache 2.0. See [LICENSE](LICENSE).

# Disclaimer

## This is not an officially supported Google product. This project is not eligible for the [Google Open Source Software Vulnerability Rewards Program](https://bughunters.google.com/open-source-security).

<a id="korean"></a>

# Gnomeregan Binary Studio

A customized fork of Vertex AI Creative Studio https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio

> ###### _이 제품은 Google에서 공식적으로 지원하는 제품이 아닙니다. 이 프로젝트는 [Google 오픈소스 소프트웨어 취약점 보상 프로그램](https://bughunters.google.com/open-source-security)의 대상이 아닙니다. 이 프로젝트는 데모 목적으로만 제공됩니다. 프로덕션 환경에서의 사용을 목적으로 하지 않습니다._

![GenMedia Creative Studio v.next](https://github.com/user-attachments/assets/da5ad223-aa6e-413c-b36e-5d63e5d5b758)

![GenMedia Creative Studio v.next](https://github.com/user-attachments/assets/61977f3c-dbb6-4002-b8c0-77d57aa03cce)

## 목차

- [GenMedia Creative Studio | Vertex AI](#genmedia-creative-studio--vertex-ai)
- [목차](#목차)
- [GenMedia Creative Studio](#genmedia-creative-studio-1)
  - [실험 기능](#실험-기능)
- [GenMedia Creative Studio 배포하기](#genmedia-creative-studio-배포하기)
  - [사전 요구사항](#사전-요구사항)
    - [1. 프로젝트 소스 코드 다운로드](#1-프로젝트-소스-코드-다운로드)
    - [2. 환경 변수 내보내기](#2-환경-변수-내보내기)
  - [사용자 지정 도메인으로 배포하기](#사용자-지정-도메인으로-배포하기)
    - [1. Terraform 초기화](#1-terraform-초기화)
    - [2. 도메인 이름에 대한 DNS A 레코드 생성](#2-도메인-이름에-대한-dns-a-레코드-생성)
    - [3. 컨테이너 이미지 빌드 및 배포](#3-컨테이너-이미지-빌드-및-배포)
    - [4. 인증서가 프로비저닝 상태가 될 때까지 대기](#4-인증서가-프로비저닝-상태가-될-때까지-대기)
  - [Cloud Run 도메인을 사용하여 배포하기](#cloud-run-도메인을-사용하여-배포하기)
    - [1. Terraform 초기화](#1-terraform-초기화-1)
    - [2. 컨테이너 이미지 빌드 및 배포](#2-컨테이너-이미지-빌드-및-배포-1)
    - [3. 초기 사용자 액세스를 제공하도록 Cloud Run의 IAP 정책 편집](#3-초기-사용자-액세스를-제공하도록-cloud-run의-iap-정책-편집)
  - [테스트를 위해 Cloud Shell에 배포하기](#테스트를-위해-cloud-shell에-배포하기)
- [추가 사용자 추가](#추가-사용자-추가)
- [솔루션 설계](#솔루션-설계)
  - [로드 밸런서와 Identity Aware Proxy를 사용한 사용자 지정 도메인](#로드-밸런서와-identity-aware-proxy를-사용한-사용자-지정-도메인)
  - [Cloud Run과 Identity Aware Proxy를 사용한 Cloud Run 도메인](#cloud-run과-identity-aware-proxy를-사용한-cloud-run-도메인)
  - [솔루션 구성 요소](#솔루션-구성-요소)
    - [런타임 구성 요소](#런타임-구성-요소)
    - [빌드 타임 구성 요소](#빌드-타임-구성-요소)
  - [개발 환경 설정](#개발-환경-설정)
    - [Python 가상 환경](#python-가상-환경)
    - [애플리케이션 환경 변수](#애플리케이션-환경-변수)
  - [GenMedia Creative Studio - 개발](#genmedia-creative-studio---개발)
    - [실행](#실행)
    - [개발](#개발-1)
  - [변경 사항 기여](#변경-사항-기여)
  - [라이선스](#라이선스)
- [면책 조항](#면책-조항)

## GenMedia Creative Studio

> **브라우저 호환성:** 최상의 경험을 위해 Google Chrome을 사용하는 것을 권장합니다. Safari나 Firefox와 같은 다른 브라우저에서는 일부 기능이 예상대로 작동하지 않을 수 있습니다.

GenMedia Creative Studio는 Google Cloud의 생성형 미디어(Veo, Lyria, Chirp, Gemini 2.5 Flash 이미지 생성(nano-banana), Gemini TTS)와 창의적 탐색 및 영감을 위한 맞춤형 워크플로 및 기술을 보여주는 웹 애플리케이션입니다. 여러분이 무엇을 만들어낼지 기대됩니다!

현재 기능 세트:

- 이미지: Imagen 3, Imagen 4, 가상 착용(Virtual Try-On), Gemini 2.5 Flash 이미지 생성
- 비디오: Veo 2, Veo 3
- 음악: Lyria
- 음성: Chirp 3 HD, Gemini Text to Speech
- 워크플로: 캐릭터 일관성, 샵 더 룩(Shop the Look), 스타터 팩 무드보드, 인테리어 디자이너, Cartoon Pro
- 자산 라이브러리

이 애플리케이션은 Google에서 빠른 AI 앱 개발을 위해 사용하는 오픈 소스 Python 프레임워크인 [Mesop](https://mesop-dev.github.io/mesop/)과 [Studio 스타일 앱용 스캐폴드](https://github.com/ghchinoy/studio-scaffold)를 사용하여 구축되었습니다.

## 실험 기능

[실험 폴더](./experiments/)에는 생성형 AI의 최첨단 기능을 보여주는 다양한 독립 실행형 애플리케이션과 새롭고 곧 출시될 기능이 포함되어 있습니다.

다음은 포함된 내용의 일부입니다:

**MCP 도구**

- **Genmedia용 MCP 도구:** 에이전트에 창의성을 부여하기 위한 Veo, Imagen, Lyria, Chirp, Gemini용 Model Context Protocol 서버입니다.

**통합 워크플로**

- **카운트다운 워크플로:** 브랜드 카운트다운 비디오를 생성하기 위한 자동화된 2단계 파이프라인입니다.
- **Storycraft:** 텍스트 설명을 완전한 비디오 내러티브로 변환하는 AI 기반 비디오 스토리보드 생성 플랫폼입니다.
  - **크리에이티브 GenMedia 워크플로:** 고품질의 브랜드 크리에이티브 미디어를 제작하기 위한 엔드투엔드 워크플로입니다.
  - **Run, Veo, Run:** Veo 3.1을 사용한 비디오 확장과 Gemini 3의 컨텍스트 인식 기능을 사용하여 분기형 내러티브 루프를 생성하는 실시간 멀티모달 비디오 생성 실험입니다.

**프롬프트 기술**

- **Promptlandia:** 프롬프트를 분석, 다듬고 개선하기 위한 강력한 웹 앱입니다.
- **Veo 유전적 프롬프트 최적화기(Genetic Prompt Optimizer):** Veo를 위한 상위 수준의 "메타 프롬프트"를 진화시키고 다듬기 위한 자동화 시스템입니다.
- **캐릭터 및 아이템 일관성:** 비디오 장면 전반에 걸쳐 캐릭터와 아이템의 일관성을 유지하기 위한 워크플로입니다.

**이미지 생성 및 분석**

- **가상 착용(Virtual Try-On):** 대규모로 의상을 가상으로 착용해 볼 수 있는 노트북입니다.
- **Imagen 제품 재맥락화(Product Recontextualization):** 대규모 제품 이미지 재맥락화를 위한 도구입니다.
- **아레나(Arena):** 다양한 모델의 이미지를 평가하고 비교하기 위한 시각적 아레나입니다.

**오디오 및 비디오**

- **크리에이티브 팟캐스트 어시스턴트(Creative Podcast Assistant):** 생성형 미디어로 팟캐스트를 만들기 위한 노트북입니다.
- **Babel:** Chirp 3 HD 음성을 위한 실험용 앱입니다.
  ...

그 외 다수! 모든 실험에 대한 자세한 목록은 [실험 README](./experiments/README.md)를 참조하세요.

## 🤖 AI 어시스턴트

이 리포지토리는 **Google의 Gemini CLI**를 사용하여 소프트웨어 엔지니어링 작업을 자동화합니다.

- **코드 리뷰어:** 버그 및 보안 문제에 대해 PR을 자동으로 검토합니다.
- **이슈 분류:** 새 이슈를 자동으로 라벨링하고 분류합니다.
- **유지 관리자 명령:** 유지 관리자가 수동으로 검토를 트리거(`@gemini-cli /review`)하거나 질문(`@gemini-cli Explain this...`)할 수 있습니다.

에이전트 및 워크플로에 대한 자세한 문서는 [AGENTS.md](./AGENTS.md)를 참조하세요.

## GenMedia Creative Studio 배포하기

GenMedia Creative Studio의 배포는 Terraform과 Cloud Build의 조합을 사용하여 수행됩니다. Terraform은 인프라를 배포하는 데 사용되며, Cloud Build는 컨테이너 이미지를 생성하고 이를 사용하도록 Cloud Run 서비스를 업데이트하는 데 사용됩니다.

이 애플리케이션에 대해 두 가지 배포 옵션이 있습니다:

1. [사용자 지정 도메인을 사용하여 배포](#사용자-지정-도메인으로-배포하기). 다음의 경우 사용하세요:
   - 외부 ID를 지원해야 하는 경우. 포함된 Terraform 스크립트는 이를 지원하지 않지만, 스크립트를 사용자 정의할 수 있습니다.
   - 사용되는 도메인에 대해 더 많은 제어를 원하는 경우
2. [자동 생성된 Cloud Run 도메인을 사용하여 배포](#cloud-run-도메인을-사용하여-배포하기). 다음의 경우 사용하세요:
   - DNS 항목을 생성할 수 없는 경우
   - [Cloud Run용 IAP 알려진 제한 사항](https://cloud.google.com/iap/docs/enabling-cloud-run#known_limitations)이 문제가 되지 않는 경우 (예: 외부 ID 없음, Cloud CDN 지원 없음)

두 가지 방식 중 원하는 방식을 선택하여 진행하세요.

### 사전 요구사항

다음이 필요합니다:

- 기존 Google Cloud 프로젝트
- 사용자 지정 도메인을 사용하려는 경우, 프로비저닝된 로드 밸런서로 확인되는 대상 도메인에 대한 DNS A 레코드를 생성할 수 있는 권한

#### 1. 프로젝트 소스 코드 다운로드

소스 코드 다운로드

```bash
git clone https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio.git
```

#### 2. 환경 변수 내보내기

다음 환경 변수는 애플리케이션을 배포하는 데 필요한 최소한의 변수입니다.

- REGION - `us-central1`으로 설정해야 합니다. 다른 지역을 선택하기 전에 필요한 GenAI 모델을 사용할 수 있는지 [여기](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#google_model_endpoint_locations)에서 확인하세요.
- PROJECT_ID - 아래 `gcloud`를 통해 얻거나 수동으로 입력할 수 있는, 원하는 Google Cloud 프로젝트의 ID로 설정하세요.
- DOMAIN_NAME - 웹 애플리케이션에 접속하는 데 사용할 DNS 이름으로 업데이트하세요 (예: creativestudio.example.com). 이 도메인에 대해 Google Cloud 관리 인증서가 생성됩니다.
- INITIAL_USERS - 웹 애플리케이션에 대한 액세스 권한이 부여될 초기 사용자들의 이메일 주소 리스트 (예: '["admin@example.com", "user@example.com"]')

예제 값을 교체하고 아래 스크립트를 실행하세요:

```bash
export REGION=us-central1 
export PROJECT_ID=$(gcloud config get project)
export INITIAL_USERS='["admin@example.com"]'
```

## 사용자 지정 도메인으로 배포하기

GenMedia Creative Studio를 사용자 지정 도메인을 사용하여 배포하려면 다음 단계를 따르세요. 이 배포 옵션을 선택하는 경우 DNS A 레코드를 생성할 수 있어야 합니다.

### 1. Terraform 초기화

사용자 지정 도메인을 사용하므로, GenMedia Creative Studio로 이동하는 데 사용할 도메인의 DNS 이름으로 변수 하나를 더 내보내야 합니다.

```bash
export DOMAIN_NAME=creativestudio.example.com
```

명령줄이 이 README가 포함된 폴더(즉, 메인 리포지토리의 루트, /)에 있는지 확인하세요. 그런 다음 다음 명령을 사용하여 `terraform.tfvars`를 생성하세요:

```bash
cat > terraform.tfvars << EOF
project_id = "$PROJECT_ID"
initial_users = $INITIAL_USERS
domain = "$DOMAIN_NAME"
EOF

terraform init
terraform apply
```

### 2. 도메인 이름에 대한 DNS A 레코드 생성

로드 밸런서와 Google Cloud 관리 인증서는 Terraform 구성 파일에 의해 프로비저닝됩니다. 프로비저닝된 로드 밸런서의 IP 주소로 확인되는 DNS A 레코드를 생성해야 합니다. 아래는 `terraform apply` 명령 실행 시 프로비저닝된 애플리케이션 밸런서의 IP가 표시되는 샘플 출력입니다.

![Load Balancer IP Address](https://github.com/user-attachments/assets/e9d6af9a-9445-441d-b89a-04b412f9baac)

> **참고:** `terraform apply` 결과에서 `load-balancer-ip = ""`와 같이 IP 주소가 출력되지 않는 경우, 생성한 `terraform.tfvars` 파일 내에 `use_lb = true`가 포함되어 있는지 확인한 후 `terraform apply`를 다시 실행해 주세요.

Google Cloud DNS를 사용하는 경우, [여기](https://cloud.google.com/dns/docs/records)의 단계를 따르세요. Google 관리 인증서를 프로비저닝하는 데는 DNS 및 로드 밸런서 구성 변경 사항이 인터넷 전체에 전파된 시점부터 최대 60분이 소요될 수 있습니다.

> A 레코드를 생성하는 데 너무 오래 걸리는 경우(보통 15분 이상) 또는 DNS 항목이 로드 밸런서의 IP가 아닌 다른 IP 주소로 확인되는 경우, Google Cloud 관리 인증서 프로비저닝이 `FAILED_NOT_VISIBLE` 상태로 실패할 수 있습니다. 이 경우 DNS A 레코드가 올바르게 업데이트되었는지 확인하고 [여기](https://cloud.google.com/load-balancing/docs/ssl-certificates/troubleshooting?#verify_configuration_changes)의 단계를 따르세요.

### 3. 컨테이너 이미지 빌드 및 배포

이 리포지토리에 포함된 쉘 스크립트 `build.sh`는 Cloud Build에 빌드를 제출하여 애플리케이션의 컨테이너 이미지를 빌드하고 배포합니다. 다음 명령을 사용하세요:

```bash
./build.sh
```

### 4. 인증서가 프로비저닝 상태가 될 때까지 대기

인프라와 애플리케이션이 모두 배포되었으므로, 인증서 프로비저닝이 완료될 때까지 기다리면 됩니다. 상태가 "ACTIVE"로 표시되고 "In use by" 섹션이 채워지면(아래 샘플 참조) 애플리케이션을 사용할 준비가 된 것입니다. [인증서 관리자 GCP 콘솔 페이지](https://console.cloud.google.com/security/ccm/list/lbCertificates)로 이동하여 인증서를 선택하고 상태를 확인할 수 있습니다.

![Provisioned Certificate](https://github.com/user-attachments/assets/20c0fb6b-c865-40e1-a9cc-fc3b0d349184)

## Cloud Run 도메인을 사용하여 배포하기

회사 도메인에 DNS 레코드를 생성할 수 없는 경우, 엔드포인트를 보호하기 위해 IAP에 대한 미리보기 지원과 함께 자동 생성된 Cloud Run 도메인을 사용할 수도 있습니다.

> 현재 Cloud Run의 IAP 통합은 미리보기 기능이며 [서비스별 약관](https://cloud.google.com/terms/service-terms#1)의 일반 서비스 약관 섹션에 있는 "GA 전 제품 약관"의 적용을 받습니다. GA 전 기능은 "있는 그대로" 제공되며 지원이 제한될 수 있습니다. 자세한 내용은 [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을 참조하세요.

### 1. Terraform 초기화

명령줄이 이 README가 포함된 폴더(즉, 메인 리포지토리의 루트, /)에 있는지 확인하세요. 그런 다음 다음 명령을 사용하여 `terraform.tfvars`를 생성하세요:

```bash
cat > terraform.tfvars << EOF
project_id = "$PROJECT_ID"
initial_users = $INITIAL_USERS
use_lb = false
EOF

terraform init
terraform apply
```

출력되는 Cloud Run URL을 기록해 두세요. 브라우저에서 애플리케이션에 액세스하기 위해 이동할 URL입니다. 하지만 그 전에 컨테이너 이미지를 빌드하고 배포해야 합니다.

![Cloud Run URL output](https://github.com/user-attachments/assets/e8729bfb-151b-4cbc-9006-6f76f5ce713e)

### 2. 컨테이너 이미지 빌드 및 배포

이 리포지토리에 포함된 쉘 스크립트 `build.sh`는 Cloud Build에 빌드를 제출하여 애플리케이션의 컨테이너 이미지를 빌드하고 배포합니다. 다음 명령을 사용하세요:

```bash
./build.sh
```

### 3. 초기 사용자 액세스를 제공하도록 Cloud Run의 IAP 정책 편집

마지막 단계는 사용자에게 액세스 권한을 제공하도록 Cloud Run 서비스의 IAP 정책을 변경하는 것입니다. 그룹을 사용할 수도 있지만, 이 예제에서는 단일 사용자에게 액세스 권한을 부여합니다.

```bash
gcloud beta iap web add-iam-policy-binding \
--project=$PROJECT_ID \
--region=$REGION \
--member=user:$INITIAL_USER \
--role=roles/iap.httpsResourceAccessor \
--resource-type=cloud-run \
--service=creative-studio
```

축하합니다. 이제 `cloud-run-app-url` Terraform 출력에 제공된 주소로 이동할 수 있습니다.

## 테스트를 위해 Cloud Shell에 배포하기

로컬 개발 환경을 설정하지 않고 UI를 빠르게 실행하려면 이 옵션을 사용하세요. 시작하려면 Cloud Shell을 사용하고 튜토리얼 지침을 따르세요.

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio.git&cloudshell_tutorial=TUTORIAL.md)

# GenMedia Creative Studio 업데이트

GenMedia Creative Studio에 새로운 기능과 수정 사항이 추가됨에 따라 배포를 업데이트하고 싶을 것입니다. 기존 인프라를 삭제할 필요는 **없습니다**.

## 애플리케이션 코드 업데이트

애플리케이션 코드(Python 파일, UI 변경 사항)만 업데이트해야 하는 경우:

1. 리포지토리에서 최신 변경 사항을 가져옵니다:

   ```bash
   git pull
   ```

2. 빌드 스크립트를 실행합니다:

   ```bash
   ./build.sh
   ```

이 스크립트는 Cloud Build에 새 빌드를 제출하고, 새 컨테이너 이미지를 생성하고, 기존 Cloud Run 서비스를 업데이트하여 이를 사용하도록 합니다.

## 인프라 업데이트

업데이트에 Terraform 구성 변경 사항(예: 새 환경 변수, 새 Google Cloud 서비스)이 포함된 경우:

1. 최신 변경 사항을 가져옵니다:

   ```bash
   git pull
   ```

2. Terraform을 초기화하여 새로운 공급자 요구 사항을 다운로드합니다:

   ```bash
   terraform init -upgrade
   ```

3. 변경 사항을 적용합니다. Terraform은 변경된 내용만 업데이트합니다:

   ```bash
   terraform apply
   ```

# 추가 사용자 추가

IAP를 사용하는 위의 배포 옵션 중 하나를 사용할 때 추가 사용자를 추가해야 하는 경우, 해당 사용자가 애플리케이션과 생성된 이미지에 모두 액세스할 수 있도록 두 가지 조치를 취해야 합니다:

- 애플리케이션 액세스 - 사용자를 IAP에 추가합니다. 로드 밸런서를 사용하여 배포한 경우 [이 단계](https://cloud.google.com/iap/docs/managing-access#managing_access_console)를 따르고 사용자에게 _IAP-Secured Web App User_ 역할을 부여하세요. Cloud Run 제공 URL만 사용하여 배포한 경우 [이 단계](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run#manage_user_or_group_access)를 따르세요.
- 이미지 액세스 - 이미지는 각 스토리지 객체의 인증된 GCS URL을 사용하여 제공되므로 사용자에게 _Storage Object Viewer_ 역할을 부여해야 합니다. 버킷 이름은 `assets-bucket` Terraform 출력으로 확인할 수 있습니다.

> **참고:** 애플리케이션이 올바르게 작동하려면 **Cloud Run 서비스 계정**에 GCS 버킷에 대한 **`Storage Object Viewer`** (`roles/storage.objectViewer`) 역할이 있어야 합니다. 이를 통해 애플리케이션이 미디어 자산을 읽고 프록시를 통해 사용자에게 제공할 수 있습니다.

내부 및 외부 사용자 추가와 액세스 문제 해결에 대한 자세한 지침은 [사용자 관리 가이드](USER_MANAGEMENT.md)를 참조하세요.

# 자주 묻는 질문 (FAQ)

일반적인 질문과 문제 해결 팁은 [FAQ](FAQ.md)를 참조하세요.

# 솔루션 설계

이 솔루션을 배포하는 방법에는 두 가지가 있습니다. 하나는 로드 밸런서와 IAP 통합이 있는 사용자 지정 도메인을 사용하는 것입니다. 다른 하나는 Cloud Run의 기본 URL을 사용하고 IAP를 Cloud Run과 통합하는 것입니다. 아래 다이어그램은 각 옵션에 사용되는 구성 요소를 보여줍니다.

## 로드 밸런서와 Identity Aware Proxy를 사용한 사용자 지정 도메인

![Solution Design - LB IAP](https://github.com/user-attachments/assets/ad057afb-4d7c-4857-b074-427eccbfaaa0)

## Cloud Run과 Identity Aware Proxy를 사용한 Cloud Run 도메인

![Solution Design - Cloud Run IAP](https://github.com/user-attachments/assets/ec2c1e04-6890-4246-b134-9923955c0486)

위 다이어그램은 Creative Studio 솔루션을 구성하는 구성 요소를 보여줍니다. 참고 사항:

- DNS 항목은 제공된 Terraform 구성 파일의 일부로 배포되지 **않습니다**. 인증서 프로비저닝이 성공하려면 프로비저닝된 로드 밸런서의 IP 주소로 확인되는 DNS A 레코드를 생성해야 합니다.
- 사용자는 Google 계정으로 인증되며 액세스는 [Identity Aware Proxy (IAP)](https://cloud.google.com/iap/docs/managing-access)를 통해 관리됩니다. IAP는 외부 ID를 지원하며 [여기](https://cloud.google.com/iap/docs/enable-external-identities)에서 자세한 내용을 확인할 수 있습니다.

## 솔루션 구성 요소

### 런타임 구성 요소

- [로드 밸런서(Load Balancer)](https://cloud.google.com/load-balancing) - Cloud Run 호스팅 애플리케이션에 대한 HTTP 액세스를 제공합니다.

- [Identity Aware Proxy](https://cloud.google.com/security/products/iap) - 인증된 사용자 또는 그룹만 웹 애플리케이션에 액세스하도록 제한합니다.
- [Cloud Run](https://cloud.google.com/run) - Mesop 애플리케이션을 호스팅하는 데 사용되는 서버리스 컨테이너 런타임입니다.
- [Cloud Firestore](https://firebase.google.com/docs/firestore) - 이미지/비디오/오디오 메타데이터를 위한 데이터 스토어입니다. Firebase가 처음이라면 [여기](https://firebase.google.com/docs/projects/learn-more#firebase-cloud-relationship)가 좋은 시작점입니다.
- [Cloud Storage](https://cloud.google.com/storage) - 이미지/비디오/오디오 파일을 저장하는 데 버킷이 사용됩니다.

### 빌드 타임 구성 요소

- [Cloud Build](https://cloud.google.com/build) - 빌드 팩을 사용하여 컨테이너 이미지를 생성하고, Artifact Registry로 푸시하고, 최신 이미지 버전을 사용하도록 Cloud Run 서비스를 업데이트합니다. 배포를 단순화하기 위해 GitHub 프로젝트 및 트리거에 대한 연결은 Terraform으로 배포되지 않습니다. 로컬로 복제된 소스 코드는 압축되어 Cloud Storage로 푸시됩니다. 컨테이너 이미지를 빌드하는 데 사용되는 것은 이 소스 스냅샷입니다.

- [Artifact Registry](https://cloud.google.com/artifact-registry/docs/overview) - 웹 애플리케이션용 컨테이너 이미지를 저장하는 데 사용됩니다.
- [Cloud Storage](https://cloud.google.com/storage) - 빌드에 사용되는 소스의 압축 파일을 저장하는 데 버킷이 사용됩니다.

## 개발 환경 설정

### Python 가상 환경

필요한 패키지가 설치된 Python 가상 환경입니다.

[uv](https://github.com/astral-sh/uv) 가상 환경 및 패키지 관리피 사용:

```
# 가상 환경에 요구 사항 동기화
uv sync
```

이전에 이 작업을 수행한 적이 있는 경우 `uv sync --upgrade` 명령을 사용하여 패키지 버전 업그레이드를 확인할 수도 있습니다.

### 애플리케이션 환경 변수

포함된 dotenv.template을 사용하여 특정 환경 변수로 `.env` 파일을 생성하세요.

하나의 환경 변수만 필요합니다:

- `PROJECT_ID`: 귀하의 Google Cloud 프로젝트 ID, `gcloud config get project`를 통해 획득

기본값 및 사용 가능한 환경 변수 옵션은 템플릿 dotenv.template 파일을 참조하세요.

## GenMedia Creative Studio - 개발

### 실행

환경 변수가 설정되면(명령줄 또는 .env 파일):

```bash
uv run main.py
```

### 개발

이 애플리케이션이 구축된 방식에 대한 자세한 정보, 특히 [Mesop](https://mesop-dev.github.io/mesop/) 및 [Studio 스타일 앱용 스캐폴드](https://github.com/ghchinoy/studio-scaffold)에 대한 구체적인 정보는 [개발자 가이드](./DEVELOPERS_GUIDE.md)를 참조하세요.

이 앱을 개발할 때, Mesop을 제공하는 FastAPI 애플리케이션이므로 다음을 사용하세요:

```bash
uv run main.py
```

기존의 Mesop 핫 리로드 기능(예: `mesop main.py`)은 현재 완전히 사용할 수 없습니다.

## 변경 사항 기여

기여하고 싶으신가요? 의도한 변경 사항을 설명하는 이슈를 열어주세요. 또한 버그 수정은 풀 리퀘스트나 GitHub 이슈로 환영합니다.

기여 방법에 대한 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 라이선스

이 리포지토리의 코드는 Apache 2.0에 따라 라이선스가 부여됩니다. [LICENSE](LICENSE)를 참조하세요.

# 면책 조항

이 제품은 Google에서 공식적으로 지원하는 제품이 아닙니다. 이 프로젝트는 [Google 오픈소스 소프트웨어 취약점 보상 프로그램](https://bughunters.google.com/open-source-security)의 대상이 아닙니다.
