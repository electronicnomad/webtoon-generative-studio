[English](#english) | [한국어](#korean)

<a id="english"></a>

# User Management Guide

This guide details the procedures for adding users to GenMedia Creative Studio, covering two main scenarios: adding users from the same organization (Internal) and adding users from different domains (External).

## Scenario A: Adding Users from the Same Domain (Internal)

**Use Case:** You and the new users are in the same Google Cloud Organization (e.g., both have `@yourcompany.com` emails), and your project's OAuth Consent Screen is set to **Internal**.

### Steps

1.  **Update Terraform Configuration:**
    Open your `terraform.tfvars` file and add the new email addresses to the `initial_users` list.

    ```hcl
    initial_users = [
      "me@yourcompany.com",
      "colleague@yourcompany.com",
      "new_user@yourcompany.com"
    ]
    ```

2.  **Apply Changes:**
    Run the following command in your terminal to update the IAP permissions:

    ```bash
    terraform apply
    ```

    _Alternatively, you can manually add the user in the Google Cloud Console > Security > Identity-Aware Proxy > Select Resource > Add Principal > Role: `IAP-secured Web App User`._

**That's it!** Internal users do not need to be added to the OAuth "Test Users" list.

---

## Scenario B: Adding Users from Different Domains (External)

**Use Case:** You are inviting users with personal emails (`@gmail.com`) or from different organizations, and your project's User Type is set to **External**.

### Steps

1.  **Add to Test Users (Oauth Consent Screen):**
    **Critical:** Since your app is likely in "Testing" mode, you **must** manually allow each user.
    - Go to **[APIs & Services > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)**.
    - Under **Test users**, click **+ ADD USERS**.
    - Enter the email address (e.g., `guest@gmail.com`) and click **Save**.

2.  **Grant IAP Permissions:**
    Just like Scenario A, you must give them permission to pass the IAP gate.
    - Update `terraform.tfvars`:
      ```hcl
      initial_users = ["me@yourcompany.com", "guest@gmail.com"]
      ```
    - Run `terraform apply`.

### 🚨 Troubleshooting: "Error Code 11"

If external users see **"Error Code 11"** or "Invalid Request" after login, while internal users work fine, it means your **OAuth Client ID** is mismatched (stuck in Internal mode).

**The Fix:** You must manually create a new "External" OAuth Client and assign it to IAP.

1.  **Create a New Client:**
    - Go to **[APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)**.
    - Click **+ CREATE CREDENTIALS > OAuth client ID**.
    - Select **Web application**. Name it `IAP External Client`.
    - **(Crucial)** In **Authorized redirect URIs**, add this exact URL format:
      `https://iap.googleapis.com/v1/oauth/clientIds/[NEW_CLIENT_ID]:handleRedirect`
      _(Tip: Create the client first to get the ID, then edit and add the URI)._
    - Click **Save**.

2.  **Force IAP to Use New Client:**
    - Go to **[Security > Identity-Aware Proxy](https://console.cloud.google.com/security/iap)**.
    - Locate your backend resource (e.g., `creative-studio`).
    - Click the **pencil icon (✎)** (or 3-dot menu > **Edit OAuth Client**) on that row.
    - Select **"Use a different OAuth client"**.
    - Enter your **New Client ID** and **Secret**.
    - Save.

3.  **Check Brand Settings:**
    - Ensure **Support Email** and **Developer Contact Info** are set in the [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent).

---

<a id="korean"></a>

# 사용자 관리 가이드 (User Management Guide)

이 가이드는 GenMedia Creative Studio에 사용자를 추가하는 절차를 설명합니다. 같은 조직의 사용자를 추가하는 경우(내부)와 다른 도메인의 사용자를 추가하는 경우(외부) 두 가지 시나리오를 다룹니다.

## 시나리오 A: 같은 도메인 사용자 추가 (Internal)

**사용 사례:** 귀하와 새 사용자가 같은 Google Cloud 조직(예: 둘 다 `@yourcompany.com` 이메일 사용)에 속해 있고, 프로젝트의 OAuth 동의 화면이 **내부(Internal)**로 설정된 경우입니다.

### 절차

1.  **Terraform 구성 업데이트:**
    `terraform.tfvars` 파일을 열고 `initial_users` 목록에 새 이메일 주소를 추가합니다.

    ```hcl
    initial_users = [
      "me@yourcompany.com",
      "colleague@yourcompany.com",
      "new_user@yourcompany.com"
    ]
    ```

2.  **변경 사항 적용:**
    터미널에서 다음 명령어를 실행하여 IAP 권한을 업데이트합니다:

    ```bash
    terraform apply
    ```

    _대안으로, Google Cloud Console > 보안 > Identity-Aware Proxy > 리소스 선택 > 주 구성원 추가 > 역할: `IAP-secured Web App User`에서 수동으로 추가할 수도 있습니다._

**끝입니다!** 내부 사용자는 OAuth "테스트 사용자" 목록에 추가할 필요가 없습니다.

---

## 시나리오 B: 다른 도메인 사용자 추가 (External)

**사용 사례:** 개인 이메일(`@gmail.com`)이나 다른 조직의 사용자를 초대하며, 프로젝트의 사용자 유형(User Type)이 **외부(External)**로 설정된 경우입니다.

### 절차

1.  **테스트 사용자 추가 (OAuth 동의 화면):**
    **중요:** 앱이 "테스트(Testing)" 상태인 경우, 각 사용자를 **반드시** 수동으로 허용해야 합니다.
    - **[API 및 서비스 > OAuth 동의 화면](https://console.cloud.google.com/apis/credentials/consent)**으로 이동합니다.
    - **테스트 사용자(Test users)** 섹션에서 **+ ADD USERS**를 클릭합니다.
    - 이메일 주소(예: `guest@gmail.com`)를 입력하고 **저장(Save)**합니다.

2.  **IAP 권한 부여:**
    시나리오 A와 마찬가지로, 이들이 IAP 보안 문을 통과할 수 있도록 권한을 부여해야 합니다.
    - `terraform.tfvars` 업데이트:
      ```hcl
      initial_users = ["me@yourcompany.com", "guest@gmail.com"]
      ```
    - `terraform apply` 실행.

### 🚨 문제 해결: "Error Code 11"

외부 사용자가 로그인 후 **"Error Code 11"** 또는 "Invalid Request" 오류를 겪지만 내부 사용자는 잘 작동한다면, **OAuth 클라이언트 ID**가 불일치(내부용으로 고정됨)하기 때문입니다.

**해결책:** 새로운 "External" OAuth 클라이언트를 수동으로 생성하여 IAP에 할당해야 합니다.

1.  **새 클라이언트 생성:**
    - **[API 및 서비스 > 사용자 인증 정보](https://console.cloud.google.com/apis/credentials)**로 이동합니다.
    - **+ 사용자 인증 정보 만들기 > OAuth 클라이언트 ID**를 클릭합니다.
    - **웹 애플리케이션**을 선택하고 이름은 `IAP External Client` 등으로 지정합니다.
    - **(매우 중요)** **승인된 리디렉션 URI**에 아래 형식의 주소를 정확히 추가합니다:
      `https://iap.googleapis.com/v1/oauth/clientIds/[새_클라이언트_ID]:handleRedirect`
      _(팁: 클라이언트를 먼저 만들어서 ID를 확인한 다음, 다시 수정 화면으로 들어가서 이 URI를 추가하세요.)_
    - **저장**합니다.

2.  **IAP에 강제 적용:**
    - **[보안 > Identity-Aware Proxy](https://console.cloud.google.com/security/iap)**로 이동합니다.
    - 백엔드 리소스(예: `creative-studio`)를 찾습니다.
    - 해당 줄의 **연필 아이콘 (✎)** (또는 점 3개 메뉴 > **OAuth 클라이언트 수정**)을 클릭합니다.
    - **"다른 OAuth 클라이언트 사용 (Use a different OAuth client)"**을 선택합니다.
    - 방금 만든 **새 Client ID**와 **Secret**을 입력합니다.
    - 저장합니다.

3.  **브랜드 설정 확인:**
    - [OAuth 동의 화면](https://console.cloud.google.com/apis/credentials/consent)에 **지원 이메일(Support Email)**과 **개발자 연락처 정보**가 설정되어 있는지 확인하세요. 이 정보가 없으면 오류가 발생합니다.
