[English](#english) | [한국어](#korean)

<a id="english"></a>

# Frequently Asked Questions (FAQ)

## Configuration & Deployment

### Q: Can I pass a list of users or a group to the `initial_user` Terraform variable for IAP access?

**A:** No, not by default. The `initial_user` variable currently accepts only a single string (e.g., one email address). This is defined in `variables.tf` and used in `main.tf` with a hardcoded `user:` prefix.

To grant IAP access to multiple users or a group, you have two options:

#### Option 1: Use the Google Cloud Console (Recommended)

After deployment, you can manage access policies directly in the [Google Cloud Console > IAP](https://console.cloud.google.com/security/iap). This avoids modifying the Terraform code.

#### Option 2: Modify Terraform for Multiple Users

If you prefer to manage this via Terraform, you can modify the code to accept a list of users.

**1. Update `variables.tf`**
Change the `initial_user` variable to a list (or create a new variable like `additional_users`):

```hcl
variable "allowed_users" {
  description = "List of email addresses to grant IAP access"
  type        = list(string)
  default     = []
}
```

**2. Update `main.tf`**
Replace the existing `google_iap_web_iam_member` resource (or add a new one) to iterate over the list:

```hcl
resource "google_iap_web_iam_member" "multi_user_iap_access" {
  for_each = toset(var.allowed_users)

  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "user:${each.value}"
}
```

#### Option 3: Support Google Groups

The current `main.tf` hardcodes the `user:` prefix:

```hcl
member = "user:${var.initial_user}"
```

To support a Google Group, you must modify `main.tf` to use the `group:` prefix or make the prefix dynamic:

```hcl
variable "access_group" {
  description = "Google Group email for IAP access"
  type        = string
}

resource "google_iap_web_iam_member" "group_iap_access" {
  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "group:${var.access_group}"
}
```

For more details on available configuration options and environment variables, please refer to [Environment Variables](ENVIRONMENT_VARIABLES.md).

### Q: The application works, but I'm not able to see images?

**A:** If the application UI loads but images (or other media assets) are failing to display, this is usually due to one of two reasons:

**1. Missing Permissions on the Cloud Run Service Account**
The Cloud Run service account must have permission to read objects from the Google Cloud Storage bucket where assets are stored.

- **Check:** Ensure the service account used by Cloud Run (e.g., `service-creative-studio@...`) has the **`Storage Object Viewer`** role (`roles/storage.objectViewer`) on the `GENMEDIA_BUCKET` (typically `creative-studio-{project_id}-assets`).
- **Fix:** You can grant this role via the Google Cloud Console or using `gcloud`:
  ```bash
  gcloud storage buckets add-iam-policy-binding gs://<YOUR_ASSET_BUCKET> \
      --member=serviceAccount:<YOUR_SERVICE_ACCOUNT_EMAIL> \
      --role=roles/storage.objectViewer
  ```

**2. `USE_MEDIA_PROXY` Configuration**
By default, the application is configured to proxy media requests through the backend (`USE_MEDIA_PROXY=true`).

- **If `true` (Default):** The browser requests images from the application server (`/proxy/image?...`), which then fetches them from GCS. This requires the **Service Account** to have GCS access (as described above). This is the recommended setup as it avoids CORS issues.
- **If `false`:** The browser attempts to fetch images directly from the GCS bucket URL (`https://storage.googleapis.com/...`). This requires the bucket to be publicly accessible (not recommended) or the user's browser to have a valid authenticated session with Google that grants access to the bucket, AND the bucket must have a proper **CORS policy** configured to allow requests from your application's domain.

---

<a id="korean"></a>

# 자주 묻는 질문 (FAQ)

## 구성 및 배포

### Q: IAP 액세스를 위해 사용자 목록이나 그룹을 `initial_user` Terraform 변수에 전달할 수 있나요?

**A:** 아니요, 기본적으로는 불가능합니다. `initial_user` 변수는 현재 단일 문자열(예: 하나의 이메일 주소)만 허용합니다. 이는 `variables.tf`에 정의되어 있으며 `main.tf`에서 하드코딩된 `user:` 접두사와 함께 사용됩니다.

여러 사용자 또는 그룹에 IAP 액세스 권한을 부여하려면 두 가지 옵션이 있습니다:

#### 옵션 1: Google Cloud Console 사용 (권장)

배포 후 [Google Cloud Console > IAP](https://console.cloud.google.com/security/iap)에서 액세스 정책을 직접 관리할 수 있습니다. 이렇게 하면 Terraform 코드를 수정하지 않아도 됩니다.

#### 옵션 2: 여러 사용자를 위해 Terraform 수정

Terraform을 통해 이를 관리하려면 코드를 수정하여 사용자 목록을 허용하도록 할 수 있습니다.

**1. `variables.tf` 업데이트**
`initial_user` 변수를 목록으로 변경하거나 `additional_users`와 같은 새 변수를 만드세요:

```hcl
variable "allowed_users" {
  description = "List of email addresses to grant IAP access"
  type        = list(string)
  default     = []
}
```

**2. `main.tf` 업데이트**
기존 `google_iap_web_iam_member` 리소스를 교체(또는 새 리소스 추가)하여 목록을 반복하도록 합니다:

```hcl
resource "google_iap_web_iam_member" "multi_user_iap_access" {
  for_each = toset(var.allowed_users)

  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "user:${each.value}"
}
```

#### 옵션 3: Google 그룹 지원

현재 `main.tf`는 `user:` 접두사를 하드코딩합니다:

```hcl
member = "user:${var.initial_user}"
```

Google 그룹을 지원하려면 `group:` 접두사를 사용하거나 접두사를 동적으로 만들도록 `main.tf`를 수정해야 합니다:

```hcl
variable "access_group" {
  description = "Google Group email for IAP access"
  type        = string
}

resource "google_iap_web_iam_member" "group_iap_access" {
  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "group:${var.access_group}"
}
```

사용 가능한 구성 옵션 및 환경 변수에 대한 자세한 내용은 [환경 변수](ENVIRONMENT_VARIABLES.md)를 참조하세요.

### Q: 애플리케이션은 작동하지만 이미지를 볼 수 없습니다?

**A:** 애플리케이션 UI가 로드되지만 이미지(또는 기타 미디어 자산)가 표시되지 않는 경우, 일반적으로 다음 두 가지 이유 중 하나 때문입니다:

**1. Cloud Run 서비스 계정의 권한 누락**
Cloud Run 서비스 계정에는 자산이 저장된 Google Cloud Storage 버킷에서 객체를 읽을 수 있는 권한이 있어야 합니다.

- **확인:** Cloud Run에서 사용하는 서비스 계정(예: `service-creative-studio@...`)에 `GENMEDIA_BUCKET`(보통 `creative-studio-{project_id}-assets`)에 대한 **`Storage Object Viewer`** 역할(`roles/storage.objectViewer`)이 있는지 확인하세요.
- **해결:** Google Cloud Console을 통하거나 `gcloud`를 사용하여 이 역할을 부여할 수 있습니다:
  ```bash
  gcloud storage buckets add-iam-policy-binding gs://<YOUR_ASSET_BUCKET> \
      --member=serviceAccount:<YOUR_SERVICE_ACCOUNT_EMAIL> \
      --role=roles/storage.objectViewer
  ```

**2. `USE_MEDIA_PROXY` 구성**
기본적으로 애플리케이션은 백엔드를 통해 미디어 요청을 프록시하도록 구성되어 있습니다(`USE_MEDIA_PROXY=true`).

- **`true`인 경우 (기본값):** 브라우저는 애플리케이션 서버(`/proxy/image?...`)에 이미지를 요청하고, 서버는 GCS에서 이미지를 가져옵니다. 이를 위해서는 **서비스 계정**에 GCS 액세스 권한이 있어야 합니다(위에서 설명한 대로). CORS 문제를 방지하므로 권장되는 설정입니다.
- **`false`인 경우:** 브라우저는 GCS 버킷 URL(`https://storage.googleapis.com/...`)에서 직접 이미지를 가져오려고 시도합니다. 이를 위해서는 버킷이 공개적으로 액세스 가능해야 하거나(권장하지 않음), 사용자 브라우저에 버킷에 대한 액세스 권한을 부여하는 유효한 Google 인증 세션이 있어야 하며, 버킷에 애플리케이션 도메인의 요청을 허용하는 적절한 **CORS 정책**이 구성되어 있어야 합니다.
