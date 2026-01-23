[English](#english) | [한국어](#korean)

<a id="english"></a>

# Deployment & Resources Guide

This document provides detailed information about the deployment process for Gnomeregan Binary Studio and the Google Cloud resources provisioned via Terraform.

## 1. Deployment Architecture Overview

This project uses **Terraform** to manage infrastructure as code (IaC) and **Cloud Build** to automate application builds and deployments.

There are two main deployment methods:

1.  **Custom Domain**: Uses a Global Load Balancer and managed SSL certificate (Recommended for production).
2.  **Cloud Run Default Domain**: Uses the default Cloud Run URL (For testing and internal use).

Both methods verify secure access via **Identity-Aware Proxy (IAP)**.

## 2. Provisioned Resources

List of major resources defined in `infra/main.tf`.

### 2.1. Core & Networking

- **API Activation**: Automatically enables required Google Cloud APIs such as `iap`, `compute`, `run`, `cloudbuild`, `aiplatform`, `firestore`, etc.
- **Service Accounts**:
  - `iap-sa`: For Identity-Aware Proxy (IAP) service.
  - `vertex-sa`: For Vertex AI service.
- **IAM Bindings**:
  - **IAP Access**: Grants `roles/iap.httpsResourceAccessor` permission to the initial users (`var.initial_users`).
  - **Cloud Run Invoker**: Grants Cloud Run invoker permission to the IAP service account.

### 2.2. Compute

- **Cloud Run Service**: `creative-studio`
  - **CPU**: 1000m (1 vCPU)
  - **Memory**: 1024Mi
  - **Scaling**: Max instances 1 (default)
  - **Environment Variables**: Automatically injects Project ID, Region, Model IDs, Bucket Name, etc.

### 2.3. Load Balancer - _Optional (`use_lb = true`)_

- **External Managed Load Balancer**: Handles HTTPS traffic.
- **Managed SSL Certificate**: Google-managed SSL certificate (uses `var.domain`).
- **Serverless NEG**: Connects Cloud Run as a backend.

### 2.4. Storage & Database

- **Cloud Storage Bucket**: `creative-studio-{project_id}-assets`
  - Stores generated image, video, and audio assets.
  - CORS Configuration: Allows requests from local development environments and deployed domains.
  - Permissions: Grants read/write permissions to the Cloud Run service account.
- **Firestore Database**: `create-studio-asset-metadata`
  - Stores metadata for generated media.
  - **Indexes**: Automatically creates composite indexes based on timestamp, media type, and user email.
- **Artifact Registry**: `creative-studio`
  - Docker container image repository.

### 2.5. Security & Build

- **Service Accounts**:
  - `service-creative-studio`: Runtime service account (used by Cloud Run).
  - `builds-creative-studio`: Build service account (used by Cloud Build).
- **Cloud Storage (Source)**: Bucket for storing build source code (`run-resources-...`).

### 2.6. Feature Specifics

- **Cartoon Pro**: Uses `genmedia_datasets` collection in Firestore. No additional infrastructure required.
- **Library V2**: Uses composite indexes (deployed via `firestore.indexes.json` if managed, or auto-created).

## 3. Step-by-Step Deployment

### Step 1: Environment Setup & Terraform Initialization

1.  Download source code and navigate to the directory.
2.  Create `terraform.tfvars` file (configure Project ID, Region, Initial Users list, Domain, etc.).
3.  `terraform init`: Download Terraform plugins and modules.

### Step 2: Infrastructure Provisioning (Terraform Apply)

Command: `terraform apply`

**What happens in this step:**

1.  Google Cloud APIs are enabled.
2.  Required service accounts are created and permissions (IAM) are granted.
3.  Network resources (LB, IAP, etc.) are configured.
4.  Database (Firestore) and Storage (GCS) are created.
5.  Cloud Run service is created with a _Placeholder_ image. (Actual app code is not deployed yet)

### Step 3: Application Build & Deployment (Build Script)

Command: `./build.sh`

**What happens in this step:**

1.  Local source code is compressed and uploaded to Cloud Storage.
2.  **Cloud Build** is triggered.
3.  Builds the container image based on `Dockerfile`.
4.  Pushes the built image to **Artifact Registry**.
5.  Updates the existing **Cloud Run** service to use the new image.

### Step 4: Access & Verification

- **Custom Domain**: Access via the configured domain after DNS setup is complete and SSL certificate is issued (may take up to 60 minutes).
- **Cloud Run Domain**: Access via the URL shown in Terraform output (`cloud-run-app-url`). The initial users must log in with their Google account via IAP.

---

<a id="korean"></a>

# 배포 및 리소스 가이드 (Deployment & Resources Guide)

이 문서는 Gnomeregan Binary Studio의 배포 프로세스와 Terraform을 통해 프로비저닝되는 Google Cloud 리소스에 대한 상세 정보를 제공합니다.

## 1. 배포 아키텍처 개요

이 프로젝트는 **Terraform**을 사용하여 인프라를 코드(IaC)로 관리하고, **Cloud Build**를 사용하여 애플리케이션 빌드 및 배포를 자동화합니다.

배포 방식은 크게 두 가지로 나뉩니다:

1.  **사용자 지정 도메인 (Custom Domain)**: Global Load Balancer와 관리형 SSL 인증서를 사용 (프로덕션 권장)
2.  **Cloud Run 기본 도메인**: Cloud Run의 기본 URL 사용 (테스트 및 내부 사용)

두 방식 모두 **Identity-Aware Proxy (IAP)** 를 통해 보안 접근을 제어합니다.

## 2. 프로비저닝되는 리소스 (Provisioned Resources)

`infra/main.tf`에 정의된 주요 리소스 목록입니다.

### 2.1. 핵심 및 네트워킹 (Core & Networking)

- **API 활성화**: `iap`, `compute`, `run`, `cloudbuild`, `aiplatform`, `firestore` 등 필요한 Google Cloud API를 자동으로 활성화합니다.
- **Service Accounts (서비스 계정)**:
  - `iap-sa`: IAP(Identity-Aware Proxy) 서비스용
  - `vertex-sa`: Vertex AI 서비스용
- **IAM Bindings**:
  - **IAP Access**: 초기 사용자들(`var.initial_users`)에게 `roles/iap.httpsResourceAccessor` 권한 부여
  - **Cloud Run Invoker**: IAP 서비스 계정에 Cloud Run 호출 권한 부여

### 2.2. 컴퓨팅 (Compute)

- **Cloud Run Service**: `creative-studio`
  - **CPU**: 1000m (1 vCPU)
  - **Memory**: 1024Mi
  - **Scaling**: 최대 인스턴스 1개 (기본값)
  - **환경 변수**: Project ID, Region, Model IDs, Bucket Name 등 설정 자동 주입

### 2.3. 로드 밸런서 (Load Balancer) - _옵션 (`use_lb = true`)_

- **External Managed Load Balancer**: HTTPS 트래픽 처리
- **Managed SSL Certificate**: Google 관리형 SSL 인증서 (`var.domain` 사용)
- **Serverless NEG**: Cloud Run을 백엔드로 연결

### 2.4. 스토리지 및 데이터베이스 (Storage & Database)

- **Cloud Storage Bucket**: `creative-studio-{project_id}-assets`
  - 생성된 이미지, 비디오, 오디오 자산 저장
  - CORS 설정: 로컬 개발 환경 및 배포된 도메인 허용
  - 권한: Cloud Run 서비스 계정에 읽기/쓰기 권한 부여
- **Firestore Database**: `create-studio-asset-metadata` (`create-studio-asset-metadata` DB)
  - 생성된 미디어의 메타데이터 저장
  - **Indexes**: 타임스탬프, 미디어 타입, 사용자 이메일 기반의 복합 인덱스 자동 생성
- **Artifact Registry**: `creative-studio`
  - Docker 컨테이너 이미지 저장소

### 2.5. 보안 및 빌드 (Security & Build)

- **Service Accounts**:
  - `service-creative-studio`: 런타임 서비스 계정 (Cloud Run에서 사용)
  - `builds-creative-studio`: 빌드용 서비스 계정 (Cloud Build에서 사용)
- **Cloud Storage (Source)**: 빌드 소스 코드 저장용 버킷 (`run-resources-...`)

### 2.6. 기능별 특이사항 (Feature Specifics)

- **Cartoon Pro**: Firestore의 `genmedia_datasets` 컬렉션을 사용합니다. 추가 인프라가 필요하지 않습니다.
- **Library V2**: 복합 인덱스(Composite Indexes)를 사용합니다 (`firestore.indexes.json`을 통해 배포되거나 자동 생성됨).

## 3. 단계별 배포 절차 (Step-by-Step Deployment)

### 1단계: 환경 설정 및 Terraform 초기화

1.  소스 코드 다운로드 및 디렉토리 이동
2.  `terraform.tfvars` 파일 생성 (프로젝트 ID, 리전, 초기 사용자 목록, 도메인 등 설정)
3.  `terraform init`: Terraform 플러그인 및 모듈 다운로드

### 2단계: 인프라 프로비저닝 (Terraform Apply)

명령어: `terraform apply`

**이 단계에서 일어나는 일:**

1.  Google Cloud API들이 활성화됩니다.
2.  필요한 서비스 계정들이 생성되고 권한(IAM)이 부여됩니다.
3.  네트워크 리소스(LB, IAP 등)가 구성됩니다.
4.  데이터베이스(Firestore)와 스토리지(GCS)가 생성됩니다.
5.  Cloud Run 서비스가 _Placeholder(임시)_ 이미지로 생성됩니다. (아직 실제 앱 코드는 배포되지 않음)

### 3단계: 애플리케이션 빌드 및 배포 (Build Script)

명령어: `./build.sh`

**이 단계에서 일어나는 일:**

1.  로컬 소스 코드를 압축하여 Cloud Storage에 업로드합니다.
2.  **Cloud Build**가 트리거됩니다.
3.  `Dockerfile`을 기반으로 컨테이너 이미지를 빌드합니다.
4.  빌드된 이미지를 **Artifact Registry**에 푸시합니다.
5.  기존에 생성된 **Cloud Run** 서비스가 새 이미지를 사용하도록 업데이트합니다.

### 4단계: 접속 및 확인

- **사용자 지정 도메인**: DNS 설정이 완료되고 SSL 인증서가 발급(최대 60분 소요)된 후 설정한 도메인으로 접속합니다.
- **Cloud Run 도메인**: Terraform 출력(`cloud-run-app-url`)에 표시된 URL로 접속합니다. 초기 사용자들은 IAP를 통해 Google 계정으로 로그인해야 합니다.
