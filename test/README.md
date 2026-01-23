[English](#english) | [한국어](#korean)

<a id="english"></a>

# Running Tests

This directory contains the automated tests for the Gearframe Creative Studio application.

## Running All Tests

To run all tests, simply execute the following command from the root of the project:

```bash
pytest
```

## Running Individual Tests

To run a specific test file, simply pass the path to the file as an argument to the `pytest` command:

```bash
pytest test/test_portraits.py
```

This is useful for focusing on a specific area of the application during development and debugging.

## Integration Tests

This suite includes integration tests that make real API calls to Google Cloud services. These tests are marked with the `integration` marker and are skipped by default to keep the standard test run fast and free of external dependencies.

To run only the integration tests, use the `-m` flag:

```bash
pytest -m integration -v -s
```

**Note:** These tests require valid Google Cloud authentication and will incur costs for the API calls made.

## Configuring the GCS Bucket

Several tests require access to Google Cloud Storage (GCS) to load test assets (e.g., images for VTO and Motion Portraits). To ensure these tests can run in different environments, the GCS bucket is configurable.

You can specify the GCS bucket to use with the `--gcs-bucket` command-line option. If you do not provide this option, the tests will default to using `gs://genai-blackbelt-fishfooding-assets`.

### Example

To run the tests using a custom GCS bucket, use the following command:

```bash
pytest --gcs-bucket gs://your-custom-test-bucket
```

This allows developers to use their own GCS resources without modifying the test code, making collaboration easier and more reliable.

## Standalone Tests

In addition to the `pytest` suite, this directory also contains standalone scripts for direct, simple testing of the VEO models:

-   `veo2_simple.py`: A script for testing the core functionalities of the Veo 2 model.
-   `veo3_simple.py`: A script for testing the core functionalities of the Veo 3 model.

These scripts can be run directly from the command line and are useful for quick, ad-hoc testing of the models without the overhead of the full test suite.

---

<a id="korean"></a>

# 테스트 실행

이 디렉토리에는 Gearframe Creative Studio 애플리케이션에 대한 자동화된 테스트가 포함되어 있습니다.

## 모든 테스트 실행

모든 테스트를 실행하려면 프로젝트 루트에서 다음 명령을 실행하면 됩니다:

```bash
pytest
```

## 개별 테스트 실행

특정 테스트 파일을 실행하려면 `pytest` 명령에 파일 경로를 인수로 전달하면 됩니다:

```bash
pytest test/test_portraits.py
```

이는 개발 및 디버깅 중에 애플리케이션의 특정 영역에 집중할 때 유용합니다.

## 통합 테스트

이 제품군에는 Google Cloud 서비스에 실제 API 호출을 수행하는 통합 테스트가 포함되어 있습니다. 이러한 테스트는 `integration` 마커로 표시되며 표준 테스트 실행을 빠르고 외부 종속성 없이 유지하기 위해 기본적으로 건너뜁니다.

통합 테스트만 실행하려면 `-m` 플래그를 사용하세요:

```bash
pytest -m integration -v -s
```

**참고:** 이러한 테스트는 유효한 Google Cloud 인증이 필요하며 API 호출에 대한 비용이 발생합니다.

## GCS 버킷 구성

여러 테스트는 테스트 자산(예: VTO 및 Motion Portraits용 이미지)을 로드하기 위해 Google Cloud Storage(GCS)에 액세스해야 합니다. 이러한 테스트가 다양한 환경에서 실행될 수 있도록 GCS 버킷을 구성할 수 있습니다.

`--gcs-bucket` 명령줄 옵션을 사용하여 사용할 GCS 버킷을 지정할 수 있습니다. 이 옵션을 제공하지 않으면 테스트는 기본적으로 `gs://genai-blackbelt-fishfooding-assets`를 사용합니다.

### 예시

사용자 지정 GCS 버킷을 사용하여 테스트를 실행하려면 다음 명령을 사용하세요:

```bash
pytest --gcs-bucket gs://your-custom-test-bucket
```

이를 통해 개발자는 테스트 코드를 수정하지 않고도 자체 GCS 리소스를 사용할 수 있어 협업이 더 쉽고 안정적입니다.

## 독립 실행형 테스트

`pytest` 제품군 외에도 이 디렉토리에는 VEO 모델의 직접적이고 간단한 테스트를 위한 독립 실행형 스크립트도 포함되어 있습니다:

-   `veo2_simple.py`: Veo 2 모델의 핵심 기능을 테스트하기 위한 스크립트입니다.
-   `veo3_simple.py`: Veo 3 모델의 핵심 기능을 테스트하기 위한 스크립트입니다.

이러한 스크립트는 명령줄에서 직접 실행할 수 있으며 전체 테스트 제품군의 오버헤드 없이 모델을 빠르고 임시적으로 테스트하는 데 유용합니다.