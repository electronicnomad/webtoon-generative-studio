[English](#english) | [한국어](#korean)

<a id="english"></a>

# Frequently Asked Questions (FAQ)

## Configuration & Deployment

### Q: How do I manage user access, add multiple users, or handle IAP errors?

**A:** User management, including adding multiple users via Terraform and troubleshooting IAP-specific issues like "Error Code 11", has been centralized in the **[Deployment & Resources Guide (DEPLOY.md) > 4. User Management](DEPLOY.md#user-management)**.

### Q: The application works, but I'm not able to see images?

**A:** If the application UI loads but images (or other media assets) are failing to display, this is usually due to one of two reasons:

**1. Missing Permissions on the Cloud Run Service Account**
The Cloud Run service account must have permission to read objects from the Google Cloud Storage bucket where assets are stored.

- **Check:** Ensure the service account used by Cloud Run (e.g., `service-creative-studio@...`) has the **`Storage Object Viewer`** role (`roles/storage.objectViewer`) on the `GENMEDIA_BUCKET`.
- **Fix:** You can grant this role via the Google Cloud Console or using `gcloud`:
  ```bash
  gcloud storage buckets add-iam-policy-binding gs://<YOUR_ASSET_BUCKET> \
      --member=serviceAccount:<YOUR_SERVICE_ACCOUNT_EMAIL> \
      --role=roles/storage.objectViewer
  ```

**2. `USE_MEDIA_PROXY` Configuration**
By default, the application is configured to proxy media requests through the backend (`USE_MEDIA_PROXY=true`).

- **If `true` (Default):** The browser requests images from the application server (`/proxy/image?...`), which then fetches them from GCS. This requires the **Service Account** to have GCS access. This is the recommended setup as it avoids CORS issues.
- **If `false`:** The browser attempts to fetch images directly from GCS. This requires the bucket to have a proper **CORS policy** configured and potentially broader access permissions.

---

<a id="korean"></a>

# 자주 묻는 질문 (FAQ)

## 구성 및 배포

### Q: 사용자 액세스를 관리하거나, 여러 사용자를 추가하거나, IAP 오류를 해결하려면 어떻게 해야 하나요?

**A:** Terraform을 통한 다수 사용자 추가 및 "Error Code 11"과 같은 IAP 관련 문제 해결을 포함한 모든 사용자 관리 절차는 **[배포 및 리소스 가이드 (DEPLOY.md) > 4. 사용자 관리](DEPLOY.md#user-management-1)** 섹션에 통합되었습니다.

### Q: 애플리케이션은 작동하지만 이미지를 볼 수 없습니다?

**A:** 애플리케이션 UI가 로드되지만 이미지(또는 기타 미디어 자산)가 표시되지 않는 경우, 일반적으로 다음 두 가지 이유 중 하나 때문입니다:

**1. Cloud Run 서비스 계정의 권한 누락**
Cloud Run 서비스 계정에는 자산이 저장된 Google Cloud Storage 버킷에서 객체를 읽을 수 있는 권한이 있어야 합니다.

- **확인:** Cloud Run에서 사용하는 서비스 계정(예: `service-creative-studio@...`)에 `GENMEDIA_BUCKET`에 대한 **`Storage Object Viewer`** 역할(`roles/storage.objectViewer`)이 있는지 확인하세요.
- **해결:** Google Cloud Console을 통하거나 `gcloud`를 사용하여 이 역할을 부여할 수 있습니다:
  ```bash
  gcloud storage buckets add-iam-policy-binding gs://<YOUR_ASSET_BUCKET> \
      --member=serviceAccount:<YOUR_SERVICE_ACCOUNT_EMAIL> \
      --role=roles/storage.objectViewer
  ```

**2. `USE_MEDIA_PROXY` 구성**
기본적으로 애플리케이션은 백엔드를 통해 미디어 요청을 프록시하도록 구성되어 있습니다(`USE_MEDIA_PROXY=true`).

- **`true`인 경우 (기본값):** 브라우저는 애플리케이션 서버(`/proxy/image?...`)에 이미지를 요청하고, 서버는 GCS에서 이미지를 가져옵니다. 이를 위해서는 **서비스 계정**에 GCS 액세스 권한이 있어야 합니다. CORS 문제를 방지하므로 권장되는 설정입니다.
- **`false`인 경우:** 브라우저는 GCS 버킷에서 직접 이미지를 가져오려고 시도합니다. 이 경우 버킷에 적절한 **CORS 정책**이 구성되어 있어야 하며, 추가적인 권한 설정이 필요할 수 있습니다.