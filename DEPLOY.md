[English](#english) | [한국어](#korean)

<a id="english"></a>

# Deploying Gearframe Creative Studio

Deployment of Gearframe Creative Studio is accomplished using a combination of **Terraform** and **Cloud Build**. Terraform is used to deploy the infrastructure and Cloud Build is used to create the container image and update the Cloud Run service.

You have two deployment options:

1.  [**Custom Domain (Recommended)**](#option-1-deploying-with-custom-domain): Use this if you need external identities or prefer a branded domain (e.g., `studio.example.com`).
2.  [**Cloud Run Domain (Quick Start)**](#option-2-deploying-using-cloud-run-domain): Use this for quick testing. Uses the default `run.app` URL.

---

### Prerequisites

1.  **Google Cloud Project**: You need an existing project.
2.  **Domain (Optional)**: If using Option 1, you need permission to create a DNS A record.

### 1. Download the Source

```bash
git clone <your-repo-url>
cd gearframe-creative-studio
```

### 2. Export Environment Variables

Set the common variables used by the deployment scripts.

```bash
# Set your Project ID and Region
export PROJECT_ID=$(gcloud config get project)
export REGION=us-central1

# Set the initial admin email (yourself)
export INITIAL_USER=admin@example.com

# (Option 1 Only) Set your target domain
export DOMAIN_NAME=studio.example.com
```

---

<a id="option-1"></a>
## Option 1: Deploying with Custom Domain

### 1. Initialize Terraform

Create the `terraform.tfvars` file with your configuration.

```bash
cat > terraform.tfvars << EOF
project_id    = "$PROJECT_ID"
region        = "$REGION"
initial_users = ["$INITIAL_USER"]
domain        = "$DOMAIN_NAME"
use_lb        = true
EOF

terraform init
terraform apply
```

If you intend to register multiple users, refer to [User Management](#userManagement) in this document.


### 2. Update DNS Records
After `terraform apply` completes, it will output the **Load Balancer IP** (e.g., `34.xxx.xxx.xxx`).
Create a **DNS A Record** for your domain pointing to this IP.

### 3. Build and Deploy Application
Run the build script to deploy the actual application code.

```bash
./build.sh
```

### 4. Wait for SSL Certificate
It may take up to **60 minutes** for the Google-managed SSL certificate to be provisioned. Once active, your site will be accessible at `https://$DOMAIN_NAME`.

---

<a id="option-2"></a>
## Option 2: Deploying using Cloud Run Domain

### 1. Initialize Terraform

Configure Terraform to skip the Load Balancer (`use_lb = false`).

```bash
cat > terraform.tfvars << EOF
project_id    = "$PROJECT_ID"
region        = "$REGION"
initial_users = ["$INITIAL_USER"]
use_lb        = false
EOF

terraform init
terraform apply
```

Note the `cloud_run_app_url` from the output.

### 2. Build and Deploy Application

```bash
./build.sh
```

### 3. Grant Access (IAP)

For Cloud Run domain deployment, you must explicitly bind the IAP policy.

```bash
gcloud beta iap web add-iam-policy-binding \
    --project=$PROJECT_ID \
    --region=$REGION \
    --member=user:$INITIAL_USER \
    --role=roles/iap.httpsResourceAccessor \
    --resource-type=cloud-run \
    --service=creative-studio
```

You can now access the application at your Cloud Run URL.

---

## Updating the Application

To deploy code changes (Python/CSS/JS) without changing infrastructure:

```bash
./build.sh
```

To update infrastructure (e.g., changed environment variables):

```bash
git pull
terraform apply
```

<a id="userManagement"></a>

## User Management

This section details how to add users to Gearframe Creative Studio.

### Scenario A: Adding Users from Same Domain (Internal)

**Use Case:** New users are in the same Google Cloud Organization (e.g., both `@yourcompany.com`) and project is **Internal**.

1.  **Update `terraform.tfvars`**: Add emails to the `initial_users` list.
    ```hcl
    initial_users = ["admin@example.com", "colleague@example.com"]
    ```
2.  **Apply Changes**:
    ```bash
    terraform apply
    ```

### Scenario B: Adding Users from Different Domains (External)

**Use Case:** Inviting `@gmail.com` users or different organizations, and project is **External**.

1.  **Add to Test Users**:
    *   Go to **[APIs & Services > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)**.
    *   Under **Test users**, click **+ ADD USERS** and add their email.
2.  **Grant IAP Permissions**: Update `terraform.tfvars` and run `terraform apply` as in Scenario A.

### 🚨 Troubleshooting: "Error Code 11"

If external users see **"Error Code 11"**, your OAuth Client ID configuration is likely incorrect (stuck in Internal mode).

**Fix**: Create a new External OAuth Client.

1.  **Create Client**:
    *   Go to **[APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)**.
    *   Create **OAuth client ID** > **Web application**.
    *   Add Redirect URI: `https://iap.googleapis.com/v1/oauth/clientIds/[CLIENT_ID]:handleRedirect`
2.  **Update IAP**:
    *   Go to **[Security > IAP](https://console.cloud.google.com/security/iap)**.
    *   Select your resource > Click **pencil icon** > **Use a different OAuth client**.
    *   Enter new Client ID and Secret.


---

<a id="korean"></a>

# 기어프레임 크리에이티브 스튜디오 배포 (Deploying Gearframe Creative Studio)

Gearframe Creative Studio는 **Terraform**으로 인프라를 구축하고, **Cloud Build**로 애플리케이션을 배포합니다.

두 가지 배포 옵션이 있습니다:

1.  [**사용자 지정 도메인 (권장)**](#option-1-kor): 외부 사용자 접근이 필요하거나 `studio.example.com` 같은 도메인을 사용하고 싶을 때 사용합니다.
2.  [**Cloud Run 도메인 (빠른 시작)**](#option-2-kor): 빠르게 테스트하고 싶을 때 사용합니다. 기본 `run.app` 주소를 사용합니다.

---

### 사전 준비 (Prerequisites)

1.  **Google Cloud 프로젝트**: 프로젝트가 생성되어 있어야 합니다.
2.  **도메인 (옵션)**: 옵션 1을 사용할 경우, DNS A 레코드를 설정할 수 있어야 합니다.

### 1. 소스 다운로드

```bash
git clone <your-repo-url>
cd gearframe-creative-studio
```

### 2. 환경 변수 설정 (Export Environment Variables)

배포 스크립트에서 공통적으로 사용할 변수를 설정합니다. 터미널에 아래 내용을 복사해서 실행하세요.

```bash
# 프로젝트 ID와 리전 설정 (기본값: us-central1)
export PROJECT_ID=$(gcloud config get project)
export REGION=us-central1

# 초기 관리자 이메일 설정 (본인 이메일)
export INITIAL_USER=admin@example.com

# (옵션 1 사용자만 해당) 사용할 도메인 주소
export DOMAIN_NAME=studio.example.com
```

---

<a id="option-1-kor"></a>
## 옵션 1: 사용자 지정 도메인으로 배포 (Custom Domain)

### 1. Terraform 초기화 및 실행

`terraform.tfvars` 설정 파일을 생성하고 인프라를 배포합니다.

```bash
cat > terraform.tfvars << EOF
project_id    = "$PROJECT_ID"
region        = "$REGION"
initial_users = ["$INITIAL_USER"]
domain        = "$DOMAIN_NAME"
use_lb        = true
EOF

terraform init
terraform apply
```

여러 사용자를 등록하려는 경우는 본 문서의 [사용자 관리](#사용자관리)를 참조하세요.

### 2. DNS 레코드 업데이트
`terraform apply`가 완료되면 출력 결과에 **Load Balancer IP**가 표시됩니다.
도메인 관리 사이트에서 해당 IP를 가리키는 **A 레코드**를 생성하세요.

### 3. 애플리케이션 빌드 및 배포
실제 애플리케이션 코드를 배포하기 위해 빌드 스크립트를 실행합니다.

```bash
./build.sh
```

### 4. SSL 인증서 발급 대기
Google 관리형 SSL 인증서가 발급되기까지 최대 **60분**이 소요될 수 있습니다. 발급이 완료되면 `https://$DOMAIN_NAME`으로 접속할 수 있습니다.

---

<a id="option-2-kor"></a>
## 옵션 2: Cloud Run 도메인으로 배포 (Cloud Run Domain)

로드 밸런서 없이 Cloud Run의 기본 주소를 사용하여 빠르게 배포합니다.

### 1. Terraform 초기화 및 실행

로드 밸런서를 사용하지 않도록(`use_lb = false`) 설정합니다.

```bash
cat > terraform.tfvars << EOF
project_id    = "$PROJECT_ID"
region        = "$REGION"
initial_users = ["$INITIAL_USER"]
use_lb        = false
EOF

terraform init
terraform apply
```

출력된 `cloud_run_app_url` 주소를 확인해 두세요.

### 2. 애플리케이션 빌드 및 배포

```bash
./build.sh
```

### 3. IAP 접근 권한 부여 (Grant Access)

Cloud Run 도메인 방식에서는 아래 명령어로 IAP 접근 권한을 명시적으로 부여해야 합니다.

```bash
gcloud beta iap web add-iam-policy-binding \
    --project=$PROJECT_ID \
    --region=$REGION \
    --member=user:$INITIAL_USER \
    --role=roles/iap.httpsResourceAccessor \
    --resource-type=cloud-run \
    --service=creative-studio
```

이제 Terraform 출력에 표시된 URL로 접속하여 로그인할 수 있습니다.

---

## 애플리케이션 업데이트 (Updating)

코드(Python, CSS, JS)만 변경되었을 때:

```bash
./build.sh
```

인프라 설정(환경 변수 등)이 변경되었을 때:

```bash
git pull
terraform apply
```

<a id="사용자관리"></a>

## 사용자 관리 (User Management)

Gearframe Creative Studio에 사용자를 추가하는 절차입니다.

### 시나리오 A: 같은 도메인 사용자 추가 (Internal)

**사용 사례:** 같은 회사(`@yourcompany.com`) 사용자이며 프로젝트가 **내부(Internal)** 로 설정된 경우.

1.  **`terraform.tfvars` 업데이트**: `initial_users` 목록에 이메일을 추가합니다.
    ```hcl
    initial_users = ["admin@example.com", "colleague@example.com"]
    ```
2.  **변경 사항 적용**:
    ```bash
    terraform apply
    ```

### 시나리오 B: 다른 도메인 사용자 추가 (External)

**사용 사례:** `@gmail.com` 등 외부 사용자이며 프로젝트가 **외부(External)** 로 설정된 경우.

1.  **테스트 사용자 추가**:
    *   **[API 및 서비스 > OAuth 동의 화면](https://console.cloud.google.com/apis/credentials/consent)** 으로 이동합니다.
    *   **Test users** 아래 **+ ADD USERS** 를 클릭하여 이메일을 추가합니다.
2.  **IAP 권한 부여**: 시나리오 A와 동일하게 `terraform.tfvars` 업데이트 후 `terraform apply`를 실행합니다.

### 🚨 문제 해결: "Error Code 11"

외부 사용자가 로그인 시 **"Error Code 11"**을 겪는다면, OAuth 클라이언트 설정 문제입니다.

**해결 방법**: 새로운 External용 OAuth 클라이언트를 생성해야 합니다.

1.  **새 클라이언트 생성**:
    *   **[API 및 서비스 > 사용자 인증 정보](https://console.cloud.google.com/apis/credentials)** 로 이동합니다.
    *   **OAuth 클라이언트 ID** > **웹 애플리케이션**을 생성합니다.
    *   승인된 리디렉션 URI에 추가: `https://iap.googleapis.com/v1/oauth/clientIds/[새_클라이언트_ID]:handleRedirect`
2.  **IAP 설정 업데이트**:
    *   **[보안 > IAP](https://console.cloud.google.com/security/iap)** 로 이동합니다.
    *   리소스 선택 > **연필 아이콘** 클릭 > **다른 OAuth 클라이언트 사용**.
    *   새 ID와 Secret 입력.
