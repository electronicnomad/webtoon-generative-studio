[English](#english) | [한국어](#korean)

<a id="english"></a>

# Agent Guidelines for veo-app

This document provides guidelines for AI agents working on the Gearframe Creative Studio codebase.

## Styling

- Prefer using shared styles from `components/styles.py` for common UI elements and layout structures.
- Page-specific or component-specific styles that are not reusable can be defined locally within those files.

## Google Cloud Storage (GCS)

- All interactions with GCS for storing media or other assets should use the `store_to_gcs` utility function located in `common/storage.py`.
- This function is configurable via `config/default.py` for bucket names.

## Configuration

- Application-level configuration values, such as model IDs, API keys (though avoid hardcoding keys directly), GCS bucket names, and feature flags, should be defined in `config/default.py`.
- Access these configurations by importing `cfg = Default()` from `config.default`.

## State Management

- Global application state (e.g., theme, user information) is managed in `state/state.py`.
- Page-specific UI state should be defined in corresponding files within the `state/` directory (e.g., `state/imagen_state.py`, `state/veo_state.py`).

## Error Handling

- For errors that occur during media generation processes and need to be communicated to the user, use the `GenerationError` custom exception defined in `common/error_handling.py`.
- Display these errors to the user via dialogs or appropriate UI elements.
- Log detailed errors to the console/server logs for debugging.

## Adding New Generative Models

- When adding a new generative model capability (e.g., a new type of image model, a different video model):
  - Add model interaction logic (API calls, request/response handling) to a new file in the `models/` directory (e.g., `models/new_model_name.py`).
  - Create UI components for controlling the new model in a subdirectory under `components/` (e.g., `components/new_model_name/generation_controls.py`).
  - Create a new page for the model in `pages/` (e.g., `pages/new_model_name.py`), utilizing the page scaffold and new components.
  - Define any page-specific state in `state/new_model_name_state.py`.
  - Add relevant configurations to `config/default.py`.
  - Update navigation in `config/navigation.json`.

## Metadata

- When storing metadata for generated media, use the `MediaItem` dataclass from `common/metadata.py` and the `add_media_item_to_firestore` function.
- Ensure all relevant fields in `MediaItem` are populated.

## Testing

- Write unit tests for utility functions and model interaction logic.
- Aim to mock external API calls during unit testing.
- Use `pytest` as the testing framework.

## Code Quality

- Use `ruff` for code formatting and linting. Ensure code is formatted (`ruff format .`) and linted (`ruff check --fix .`) before submitting changes.

## 🤖 GitHub Automation Agents

This repository uses **Google's Gemini CLI** to automate software engineering tasks. Our AI agents assist with code reviews, issue triage, and general maintenance to keep the project moving efficiently.

## Automatic Behaviors

These agents run automatically based on events in the repository.

### 🔎 Code Reviewer

- **Trigger:** When a **Pull Request** is opened.

- **Action:** The agent reviews the code changes (diff), looking for bugs, security issues, and style improvements.
- **Output:** It posts review comments directly on the PR.
- **Note:** The agent focuses on the _diff_ only and provides constructive feedback. It does not replace human review.

### 📋 Issue Triage

- **Trigger:** When a new **Issue** is opened.

- **Action:** The agent analyzes the title and body of the issue.
- **Output:** It automatically applies relevant **Labels** (e.g., `bug`, `enhancement`, `question`) to help organize the backlog.

---

## Maintainer Commands

Project maintainers (Owners, Members, Collaborators) can manually invoke the agents using comment commands.

| Command                  | Description                                                                                                                                          |
| :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@gemini-cli /review`    | Manually triggers a full code review on the current Pull Request.                                                                                    |
| `@gemini-cli /triage`    | Manually triggers label analysis on the current Issue or PR.                                                                                         |
| `@gemini-cli [question]` | Ask the agent a question about the codebase or request a specific task. <br><br> _Example:_ `@gemini-cli Explain how the authentication flow works.` |

> **Note:** These commands are restricted to project maintainers to prevent abuse and manage costs.

---

## Workflow Architecture

The automation is built on GitHub Actions using a "Router-Worker" pattern:

1. **Dispatch Router (`gemini-dispatch.yml`):** The entry point. It listens for events, validates permissions, and routes the request to the correct worker.
2. **Worker Workflows:**
   - `gemini-review.yml`: Handles code analysis.
   - `gemini-triage.yml`: Handles labeling.
   - `gemini-invoke.yml`: Handles general Q&A.

This system is powered by the [Gemini CLI](https://github.com/google-github-actions/run-gemini-cli) action.

---

<a id="korean"></a>

# veo-app을 위한 에이전트 가이드라인

이 문서는 Gearframe Creative Studio 코드베이스에서 작업하는 AI 에이전트를 위한 가이드라인을 제공합니다.

## 스타일링 (Styling)

- 일반적인 UI 요소 및 레이아웃 구조에는 `components/styles.py`의 공유 스타일을 사용하는 것을 선호하세요.
- 재사용할 수 없는 페이지별 또는 컴포넌트별 스타일은 해당 파일 내에서 로컬로 정의할 수 있습니다.

## Google Cloud Storage (GCS)

- 미디어 또는 기타 자산을 저장하기 위한 GCS와의 모든 상호 작용은 `common/storage.py`에 위치한 `store_to_gcs` 유틸리티 함수를 사용해야 합니다.
- 이 함수는 `config/default.py`를 통해 버킷 이름을 구성할 수 있습니다.

## 구성 (Configuration)

- 모델 ID, API 키(키를 직접 하드코딩하지 마세요), GCS 버킷 이름 및 기능 플래그와 같은 애플리케이션 수준 구성 값은 `config/default.py`에 정의해야 합니다.
- `config.default`에서 `cfg = Default()`를 가져와 이러한 구성에 액세스하세요.

## 상태 관리 (State Management)

- 전역 애플리케이션 상태(예: 테마, 사용자 정보)는 `state/state.py`에서 관리됩니다.
- 페이지별 UI 상태는 `state/` 디렉토리 내의 해당 파일(예: `state/imagen_state.py`, `state/veo_state.py`)에 정의해야 합니다.

## 오류 처리 (Error Handling)

- 미디어 생성 프로세스 중에 발생하여 사용자에게 전달해야 하는 오류의 경우, `common/error_handling.py`에 정의된 `GenerationError` 사용자 지정 예외를 사용하세요.
- 대화 상자 또는 적절한 UI 요소를 통해 이러한 오류를 사용자에게 표시하세요.
- 디버깅을 위해 자세한 오류를 콘솔/서버 로그에 기록하세요.

## 새로운 생성 모델 추가

- 새로운 생성 모델 기능(예: 새로운 유형의 이미지 모델, 다른 비디오 모델)을 추가할 때:
  - `models/` 디렉토리의 새 파일(예: `models/new_model_name.py`)에 모델 상호 작용 로직(API 호출, 요청/응답 처리)을 추가하세요.
  - `components/` 아래의 하위 디렉토리(예: `components/new_model_name/generation_controls.py`)에 새 모델을 제어하기 위한 UI 컴포넌트를 만드세요.
  - 페이지 스캐폴드와 새 컴포넌트를 활용하여 `pages/`에 모델을 위한 새 페이지(예: `pages/new_model_name.py`)를 만드세요.
  - `state/new_model_name_state.py`에 페이지별 상태를 정의하세요.
  - `config/default.py`에 관련 구성을 추가하세요.
  - `config/navigation.json`에서 탐색을 업데이트하세요.

## 메타데이터 (Metadata)

- 생성된 미디어의 메타데이터를 저장할 때, `common/metadata.py`의 `MediaItem` 데이터 클래스와 `add_media_item_to_firestore` 함수를 사용하세요.
- `MediaItem`의 모든 관련 필드가 채워져 있는지 확인하세요.

## 테스트 (Testing)

- 유틸리티 함수 및 모델 상호 작용 로직에 대한 단위 테스트를 작성하세요.
- 단위 테스트 중에 외부 API 호출을 모의(mock)하는 것을 목표로 하세요.
- 테스트 프레임워크로 `pytest`를 사용하세요.

## 코드 품질 (Code Quality)

- 코드 서식 지정 및 린팅에 `ruff`를 사용하세요. 변경 사항을 제출하기 전에 코드가 서식 지정(`ruff format .`)되고 린트(`ruff check --fix .`)되었는지 확인하세요.

## 🤖 GitHub 자동화 에이전트

이 리포지토리는 **Google의 Gemini CLI**를 사용하여 소프트웨어 엔지니어링 작업을 자동화합니다. AI 에이전트는 코드 리뷰, 이슈 분류 및 일반 유지 관리를 지원하여 프로젝트를 효율적으로 진행하도록 돕습니다.

## 자동 동작 (Automatic Behaviors)

이 에이전트들은 리포지토리의 이벤트를 기반으로 자동으로 실행됩니다.

### 🔎 코드 리뷰어 (Code Reviewer)

- **트리거:** **Pull Request**가 열릴 때.

- **동작:** 에이전트가 코드 변경 사항(diff)을 검토하여 버그, 보안 문제 및 스타일 개선 사항을 찾습니다.
- **출력:** PR에 직접 리뷰 코멘트를 게시합니다.
- **참고:** 에이전트는 *diff*에만 집중하고 건설적인 피드백을 제공합니다. 사람의 검토를 대체하지 않습니다.

### 📋 이슈 분류 (Issue Triage)

- **트리거:** 새 **Issue**가 열릴 때.

- **동작:** 에이전트가 이슈의 제목과 본문을 분석합니다.
- **출력:** 백로그를 정리하는 데 도움이 되도록 관련 **레이블**(예: `bug`, `enhancement`, `question`)을 자동으로 적용합니다.

---

## 유지 관리자 명령 (Maintainer Commands)

프로젝트 유지 관리자(소유자, 멤버, 협력자)는 코멘트 명령을 사용하여 수동으로 에이전트를 호출할 수 있습니다.

| 명령                  | 설명                                                                                                                                     |
| :-------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| `@gemini-cli /review` | 현재 Pull Request에 대해 전체 코드 리뷰를 수동으로 트리거합니다.                                                                         |
| `@gemini-cli /triage` | 현재 Issue 또는 PR에 대해 레이블 분석을 수동으로 트리거합니다.                                                                           |
| `@gemini-cli [질문]`  | 에이전트에게 코드베이스에 대해 질문하거나 특정 작업을 요청합니다. <br><br> _예시:_ `@gemini-cli 인증 흐름이 어떻게 작동하는지 설명해줘.` |

> **참고:** 이러한 명령은 남용을 방지하고 비용을 관리하기 위해 프로젝트 유지 관리자로 제한됩니다.

---

## 워크플로 아키텍처 (Workflow Architecture)

자동화는 "Router-Worker" 패턴을 사용하여 GitHub Actions를 기반으로 구축되었습니다:

1. **디스패치 라우터 (`gemini-dispatch.yml`):** 진입점입니다. 이벤트를 수신하고, 권한을 확인하고, 요청을 올바른 워커로 라우팅합니다.
2. **워커 워크플로:**
   - `gemini-review.yml`: 코드 분석을 처리합니다.
   - `gemini-triage.yml`: 레이블링을 처리합니다.
   - `gemini-invoke.yml`: 일반적인 Q&A를 처리합니다.

이 시스템은 [Gemini CLI](https://github.com/google-github-actions/run-gemini-cli) 액션으로 구동됩니다.
