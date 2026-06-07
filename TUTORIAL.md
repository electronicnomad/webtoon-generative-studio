[English](#english) | [한국어](#korean)

<a id="english"></a>

# Webtoon Generator: Veo 2 module Tutorial

## Welcome!

If you're seeing this, you've cloned the correct repository, and you should be in the `webtoon-generative-studio` directory! Let's get started.


## First step: auth to your Google Cloud Project

Type this command in the shell, substituting your project name

```bash
gcloud config set project YOUR_PROJECT_ID
export PROJECT_ID=$(gcloud config get project)
```

## Second steps: Project prerequisites

### Firestore

For the defaults, a Firestore database should be set up.

To check your Firestore databases (we're looking for a Standard database named "(default)"):

```bash
gcloud firestore databases list
```

If you don't have the default one, create one:

```bash
gcloud firestore databases create --database="(default)" --location=nam5
```

### Google Cloud Storage bucket

For the defaults, you should have a bucket named YOUR_PROJECT_ID-assets, and you can check by doing this:

```bash
gcloud storage ls gs://YOUR_PROJECT_ID-assets
```

If you have one, great! If not, create one:

```bash
gcloud storage buckets create -l us-central1 gs://YOUR_PROJECT_ID-assets
```

Notre

### uv

[uv](https://github.com/astral-sh/uv) is a fast Python package manager. Since this app is written in Python, we'll use this to install prerequisites.

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Third step: Start the app

Use uv to sync the prerequisites, activate the Python virtual environment, and start the app!

```bash
uv sync
source .venv/bin/activate
uv run main.py
#mesop main.py
```

If you get an error that `/` is not found, navigate to `/home`


---

<a id="korean"></a>

# Webtoon Generator: Veo 2 모듈 튜토리얼 (Tutorial)

## 환영합니다!

이 글을 보고 계시다면 올바른 리포지토리를 복제하셨으며, `webtoon-generative-studio` 디렉토리에 계실 것입니다! 시작해 봅시다.


## 첫 번째 단계: Google Cloud 프로젝트 인증

프로젝트 이름을 대체하여 쉘에 다음 명령을 입력하세요.

```bash
gcloud config set project YOUR_PROJECT_ID
export PROJECT_ID=$(gcloud config get project)
```

## 두 번째 단계: 프로젝트 사전 요구사항

### Firestore

기본적으로 Firestore 데이터베이스가 설정되어 있어야 합니다.

Firestore 데이터베이스를 확인하려면("(default)"라는 이름의 Standard 데이터베이스를 찾고 있습니다):

```bash
gcloud firestore databases list
```

기본 데이터베이스가 없는 경우 생성하세요:

```bash
gcloud firestore databases create --database="(default)" --location=nam5
```

### Google Cloud Storage 버킷

기본적으로 `YOUR_PROJECT_ID-assets`라는 이름의 버킷이 있어야 합니다. 다음을 수행하여 확인할 수 있습니다:

```bash
gcloud storage ls gs://YOUR_PROJECT_ID-assets
```

있다면 좋습니다! 없다면 생성하세요:

```bash
gcloud storage buckets create -l us-central1 gs://YOUR_PROJECT_ID-assets
```

참고

### uv

[uv](https://github.com/astral-sh/uv)는 빠른 Python 패키지 관리자입니다. 이 앱은 Python으로 작성되었으므로 전제 조건을 설치하는 데 이를 사용합니다.

```bash
# macOS 및 Linux에서.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 세 번째 단계: 앱 시작

uv를 사용하여 전제 조건을 동기화하고, Python 가상 환경을 활성화하고, 앱을 시작하세요!

```bash
uv sync
source .venv/bin/activate
uv run main.py
#mesop main.py
```

`/`를 찾을 수 없다는 오류가 발생하면 `/home`으로 이동하세요.

