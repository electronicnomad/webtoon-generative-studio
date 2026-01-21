[English](#english) | [한국어](#korean)

<a id="english"></a>

# Developer's Guide

Welcome to the GenMedia Creative Studio application! This guide provides an overview of the application's architecture, key development patterns, and a step-by-step tutorial for adding new pages. Its purpose is to help you understand the project's structure and contribute effectively.

## Application Architecture

This application is built using Python with the [Mesop](https://mesop-dev.github.io/mesop/) UI framework and a [FastAPI](https://fastapi.tiangolo.com/) backend. The project is structured to enforce a clear separation of concerns, making the codebase easier to navigate, maintain, and extend.

Here is a breakdown of the key directories and their roles:

- **`main.py`**: The main entry point of the application, responsible for initializing the FastAPI server, mounting the Mesop application, handling root-level routing, and applying global middleware.
- **`pages/`**: Contains the top-level UI code for each distinct page in the application (e.g., `/home`, `/imagen`).
- **`components/`**: Holds reusable UI components (e.g., headers, dialogs) used across multiple pages.
- **`models/`**: Contains the core business logic, including interactions with Generative AI models and databases.
- **`state/`**: Defines the application's state management classes using Mesop's `@me.stateclass`.
- **`config/`**: For application configuration, including default settings, navigation structure, and prompt templates.

### Visual Workflow

The following sequence diagram shows the typical flow for a generative AI feature in this application, using the VEO page as an example.

![veo sequence diagram](https://github.com/user-attachments/assets/9df0cece-47b0-4c0f-848a-6d6dbf24465c)

This diagram illustrates the flow:

1.  A user interaction happens in the **UI (`pages/`)**.
2.  The UI calls a function in the **business logic layer (`models/`)**.
3.  The model layer interacts with **external Google Cloud APIs**.
4.  Data is saved to **Firestore** via the metadata service (`common/metadata.py`).
5.  The **UI State (`state/`)** is updated, causing the UI to re-render and display the result.

## Core Development Patterns and Lessons Learned

This section outlines the key architectural patterns and best practices that are essential for extending this application.

### Mesop UI and State Management

1.  **Co-locating Page State:**
    - **Problem:** A page fails to load with a `NameError`.
    - **Solution:** For state that is specific to a single page, the `@me.stateclass` definition **must** be in the same file as the `@me.page` function. Only the global `AppState` should be in its own file (`state/state.py`).

2.  **Displaying Temporary Notifications with `snackbar`:**
    - **Problem:** You need to show a temporary, non-blocking notification to the user (e.g., "Saved to library" or an error message).
    - **Solution:** Use the page-local snackbar pattern. This involves three parts:
      1.  **State:** Add `show_snackbar: bool = False` and `snackbar_message: str = ""` to your page's local `@me.stateclass`.
      2.  **UI:** Add the `<snackbar>` component to your page's layout, binding it to the state variables: `snackbar(is_visible=state.show_snackbar, label=state.snackbar_message)`.
      3.  **Handler:** Create a helper generator function that manages the show/hide cycle and call it from your event handlers using `yield from`.

    - **Example Implementation:**

      ```python
      # In your pages/my_page.py

      import time
      from components.snackbar import snackbar

      @me.stateclass
      class PageState:
          # ... other state properties
          show_snackbar: bool = False
          snackbar_message: str = ""

      def page_content():
          state = me.state(PageState)
          # ... your page layout
          snackbar(is_visible=state.show_snackbar, label=state.snackbar_message)

      def show_snackbar_helper(state: PageState, message: str):
          """Helper to show and automatically hide the snackbar."""
          state.snackbar_message = message
          state.show_snackbar = True
          yield
          time.sleep(3)
          state.show_snackbar = False
          yield

      def on_some_action(e: me.ClickEvent):
          state = me.state(PageState)
          try:
              # ... do some work ...
              yield from show_snackbar_helper(state, "Action was successful!")
          except Exception as ex:
              yield from show_snackbar_helper(state, f"An error occurred: {ex}")
      ```

3.  **Correctly Handling Event Handlers:**
    - **Problem:** A UI element does not update the UI when interacted with.
    - **Solution:** The function directly assigned to an event handler (e.g., `on_click`) must be the generator function that `yield`s. Using a `lambda` to call another generator can break the UI update chain.

4.  **Introspecting Custom Components:**
    - **Problem:** A `TypeError` about an unexpected keyword argument occurs when using a component from the `components/` directory.
    - **Solution:** This project's custom components have specific APIs. If you encounter a `TypeError`, **read the component's source file** to understand its exact function signature.

5.  **Passing Data from Loops to Event Handlers:**
    - **Problem:** An event handler for an item in a list always receives data from the _last_ item.
    - **Solution:** Use the `key` property of the clickable component to pass a unique identifier. The event handler can then access this value via `e.key`.

### Composable UI for Image Uploads

- **Problem:** You need to create a UI where a user can either upload a new image or select one from the media library. This UI should display a placeholder when empty and the selected image when populated.
- **Solution:** Follow a compositional pattern by combining several small, reusable components. Do not build a single, monolithic "uploader" component for your page.

- **Core Components:**
  - **`image_thumbnail`:** Use this to display an image that has already been uploaded or selected. It includes a built-in "remove" button.
  - **`_uploader_placeholder`:** Create a private component within your page that renders a styled placeholder box. This component should contain:
    - An `me.uploader` component for local file uploads.
    - The `library_chooser_button` component for opening the media library.
  - **Page Logic:** Your main page component is responsible for the logic. It should conditionally render either the `_uploader_placeholder` (if no image is selected) or the `image_thumbnail` (if an image is selected).

- **Example Structure:**

  ```python
  # In your pages/my_page.py
  from components.image_thumbnail import image_thumbnail
  from components.library.library_chooser_button import library_chooser_button

  @me.component
  def _uploader_placeholder(on_upload, on_open_library):
      with me.box(style=...): # Dashed border style
          me.uploader(on_upload=on_upload, ...)
          library_chooser_button(on_library_select=on_open_library, ...)

  def my_page_content():
      state = me.state(PageState)
      if state.my_image_uri:
          image_thumbnail(
              image_uri=state.my_image_uri,
              on_remove=handle_remove_image,
              ...
          )
      else:
          _uploader_placeholder(
              on_upload=handle_upload,
              on_open_library=handle_open_library,
          )
  ```

### Analytics and Instrumentation

When adding new features, it is important to instrument them with the analytics framework from `common/analytics.py` to provide insights into user behavior and application performance.

#### Page Views

Page view tracking is handled automatically by the `page_scaffold` component. When creating a new page, ensure it is wrapped with this scaffold to enable automatic page view logging.

#### UI Interactions

There are two ways to track UI interactions: the `@track_click` decorator for simple button clicks, and the `log_ui_click` function for other controls.

##### Button Clicks

To track clicks on buttons, use the `@track_click` decorator on your event handler. This is the simplest way to instrument a button.

**Example:**

```python
from common.analytics import track_click

@track_click(element_id="my_page_generate_button")
def on_generate_click(e: me.ClickEvent):
    # Your event handler logic here
    yield
```

##### Other Controls

For UI elements that don't have a simple click event (e.g., sliders, selects, text inputs), you can use the `log_ui_click` function directly inside the event handler.

**Example:**

```python
from common.analytics import log_ui_click
from state.state import AppState

def on_slider_change(e: me.SliderValueChangeEvent):
    app_state = me.state(AppState)
    log_ui_click(
        element_id="my_page_slider",
        page_name=app_state.current_page,
        session_id=app_state.session_id,
        extras={"value": e.value},
    )
    # Your event handler logic here
    yield
```

#### Element IDs

When choosing an `element_id`, use a consistent naming convention. A good practice is to use the format `page_name_element_type_name`. For example:

- `imagen_generate_button`
- `veo_aspect_ratio_select`
- `chirp_text_input`

#### Model Calls

To track the performance and status of calls to generative models, use the `track_model_call` context manager.

**Example:**

```python
from common.analytics import track_model_call

with track_model_call("my-generative-model-v1", prompt_length=len(prompt)):
    model.generate_content(...)
```

## How to Add a New Page

Adding a new page to the application follows a streamlined, modular pattern that keeps page-specific logic self-contained.

### Step 1: Create the Page File

Create a new Python file in the `pages/` directory (e.g., `my_new_page.py`).

### Step 2: Define the Page Structure

Inside your new file, define the core components of your page. A typical page file includes:

1.  **State Class:** If your page has its own state, define a state class using `@me.stateclass`.
2.  **UI Content Function:** Create a function that builds the UI for your page (e.g., `my_new_page_content()`).
3.  **Page Route Function:** Create the main page entry point function, typically named `page()`, decorated with `@me.page(...)`.

**`pages/my_new_page.py`:**

```python
import mesop as me
from state.state import AppState
from components.header import header
from components.page_scaffold import page_frame, page_scaffold

@me.stateclass
class PageState:
    my_value: str = "Hello"

def my_new_page_content():
    state = me.state(PageState)
    with page_frame():
        header("My New Page", "rocket_launch")
        me.text(f"Welcome to my new page! My value is: {state.my_value}")

@me.page(
    path="/my_new_page",
    title="My New Page - GenMedia Creative Studio",
)
def page():
    with page_scaffold(page_name="my_new_page"):
        my_new_page_content()
```

### Step 3: Register the Page in `main.py`

Import your new page module in `main.py` to make it discoverable.

```python
from pages import my_new_page as my_new_page_page
```

### Step 4: Add the Page to the Navigation

Add your new page to `config/navigation.json` to make it accessible in the UI.

```json
{
  "id": 60,
  "display": "My New Page",
  "icon": "rocket_launch",
  "route": "/my_new_page",
  "group": "workflows"
}
```

---

<a id="korean"></a>

# 개발자 가이드 (Developer's Guide)

GenMedia Creative Studio 애플리케이션에 오신 것을 환영합니다! 이 가이드는 애플리케이션의 아키텍처, 주요 개발 패턴, 새로운 페이지를 추가하기 위한 단계별 튜토리얼을 제공합니다. 이 프로젝트의 구조를 이해하고 효과적으로 기여할 수 있도록 돕기 위해 작성되었습니다.

## 애플리케이션 아키텍처

이 애플리케이션은 **Python**으로 [Mesop](https://mesop-dev.github.io/mesop/) UI 프레임워크와 [FastAPI](https://fastapi.tiangolo.com/) 백엔드를 사용하여 구축되었습니다. 이 프로젝트는 관심사 분리 원칙을 준수하여 구성되었으며, 코드베이스를 쉽게 탐색, 유지 관리 및 확장할 수 있습니다.

주요 디렉토리와 역할은 다음과 같습니다:

- **`main.py`**: 애플리케이션의 메인 진입점입니다. FastAPI 서버 초기화, Mesop 애플리케이션 마운트, 루트 레벨 라우팅 처리, 전역 미들웨어 적용을 담당합니다.
- **`pages/`**: 애플리케이션의 각 페이지(예: `/home`, `/imagen`)에 대한 최상위 UI 코드를 포함합니다.
- **`components/`**: 여러 페이지에서 사용되는 재사용 가능한 UI 컴포넌트(예: 헤더, 다이얼로그)를 포함합니다.
- **`models/`**: Generative AI 모델 및 데이터베이스와의 상호 작용을 포함한 핵심 비즈니스 로직을 포함합니다.
- **`state/`**: Mesop의 `@me.stateclass`를 사용하여 애플리케이션의 상태 관리 클래스를 정의합니다.
- **`config/`**: 기본 설정, 탐색 구조, 프롬프트 템플릿을 포함한 애플리케이션 구성을 담당합니다.

### 시각적 워크플로 (Visual Workflow)

다음 시퀀스 다이어그램은 VEO 페이지를 예로 들어, 이 애플리케이션의 생성형 AI 기능에 대한 일반적인 흐름을 보여줍니다.

![veo sequence diagram](https://github.com/user-attachments/assets/9df0cece-47b0-4c0f-848a-6d6dbf24465c)

이 다이어그램은 다음 흐름을 보여줍니다:

1.  **UI (`pages/`)** 에서 사용자 상호 작용이 발생합니다.
2.  UI는 **비즈니스 로직 계층 (`models/`)** 의 함수를 호출합니다.
3.  모델 계층은 **외부 Google Cloud API**와 상호 작용합니다.
4.  메타데이터 서비스(`common/metadata.py`)를 통해 데이터가 **Firestore**에 저장됩니다.
5.  **UI 상태 (`state/`)** 가 업데이트되어 UI가 다시 렌더링되고 결과가 표시됩니다.

## 핵심 개발 패턴 및 교훈

이 섹션에서는 이 애플리케이션을 확장할 때 필수적인 주요 아키텍처 패턴과 모범 사례를 설명합니다.

### Mesop UI 및 상태 관리

1.  **페이지 상태 공동 배치 (Co-locating Page State):**
    - **문제:** `NameError`로 인해 페이지 로드에 실패합니다.
    - **해결:** 단일 페이지에 특정한 상태의 경우, `@me.stateclass` 정의는 반드시 `@me.page` 함수와 **동일한 파일**에 있어야 합니다. 전역 `AppState`만 자체 파일(`state/state.py`)에 있어야 합니다.

2.  **`snackbar`로 임시 알림 표시:**
    - **문제:** 사용자에게 일시적이고 비차단적인 알림(예: "라이브러리에 저장됨" 또는 오류 메시지)을 표시해야 합니다.
    - **해결:** 페이지 로컬 snackbar 패턴을 사용하세요. 다음 세 부분으로 구성됩니다:
      1.  **State:** 페이지 로컬 `@me.stateclass`에 `show_snackbar: bool = False` 및 `snackbar_message: str = ""`를 추가합니다.
      2.  **UI:** 페이지 레이아웃에 `<snackbar>` 컴포넌트를 추가하고 상태 변수에 바인딩합니다: `snackbar(is_visible=state.show_snackbar, label=state.snackbar_message)`.
      3.  **Handler:** show/hide 주기를 관리하는 헬퍼 제너레이터 함수를 만들고 이벤트 핸들러에서 `yield from`을 사용하여 호출합니다.

    - **구현 예시:**

      ```python
      # pages/my_page.py

      import time
      from components.snackbar import snackbar

      @me.stateclass
      class PageState:
          # ... 다른 상태 속성
          show_snackbar: bool = False
          snackbar_message: str = ""

      def page_content():
          state = me.state(PageState)
          # ... 페이지 레이아웃
          snackbar(is_visible=state.show_snackbar, label=state.snackbar_message)

      def show_snackbar_helper(state: PageState, message: str):
          """스낵바를 표시하고 자동으로 숨기는 헬퍼"""
          state.snackbar_message = message
          state.show_snackbar = True
          yield
          time.sleep(3)
          state.show_snackbar = False
          yield

      def on_some_action(e: me.ClickEvent):
          state = me.state(PageState)
          try:
              # ... 작업 수행 ...
              yield from show_snackbar_helper(state, "작업 성공!")
          except Exception as ex:
              yield from show_snackbar_helper(state, f"오류 발생: {ex}")
      ```

3.  **이벤트 핸들러의 올바른 처리:**
    - **문제:** UI 요소를 상호 작용해도 UI가 업데이트되지 않습니다.
    - **해결:** 이벤트 핸들러(예: `on_click`)에 직접 할당된 함수는 `yield`하는 제너레이터 함수여야 합니다. `lambda`를 사용하여 다른 제너레이터를 호출하면 UI 업데이트 체인이 끊어질 수 있습니다.

4.  **사용자 지정 컴포넌트 내부 확인:**
    - **문제:** `components/` 디렉토리의 컴포넌트를 사용할 때 예상치 못한 키워드 인수에 대한 `TypeError`가 발생합니다.
    - **해결:** 이 프로젝트의 사용자 지정 컴포넌트는 특정 API를 가지고 있습니다. `TypeError`가 발생하면 해당 **컴포넌트의 소스 파일**을 읽어 정확한 함수 시그니처를 이해하세요.

5.  **루프에서 이벤트 핸들러로 데이터 전달:**
    - **문제:** 목록 항목의 이벤트 핸들러가 항상 _마지막_ 항목의 데이터만 수신합니다.
    - **해결:** 클릭 가능한 컴포넌트의 `key` 속성을 사용하여 고유 식별자를 전달하세요. 이벤트 핸들러는 `e.key`를 통해 이 값에 액세스할 수 있습니다.

### 이미지 업로드를 위한 구성 가능한 UI (Composable UI)

- **문제:** 사용자가 새 이미지를 업로드하거나 미디어 라이브러리에서 이미지를 선택할 수 있는 UI를 만들어야 합니다. 비어 있을 때는 플레이스홀더를, 채워지면 선택된 이미지를 표시해야 합니다.
- **해결:** 여러 개의 작고 재사용 가능한 컴포넌트를 결합하여 구성 패턴을 따르세요. 페이지를 위한 하나의 거대한 "업로더" 컴포넌트를 만들지 마세요.

- **핵심 컴포넌트:**
  - **`image_thumbnail`:** 이미 업로드되거나 선택된 이미지를 표시하는 데 사용하세요. "제거" 버튼이 내장되어 있습니다.
  - **`_uploader_placeholder`:** 스타일이 적용된 플레이스홀더 박스를 렌더링하는 전용 컴포넌트를 페이지 내에 만드세요. 이 컴포넌트는 다음을 포함해야 합니다:
    - 로컬 파일 업로드를 위한 `me.uploader` 컴포넌트.
    - 미디어 라이브러리를 열기 위한 `library_chooser_button` 컴포넌트.
  - **페이지 로직:** 메인 페이지 컴포넌트가 로직을 담당합니다. 이미지가 선택되지 않은 경우 `_uploader_placeholder`를, 이미지가 선택된 경우 `image_thumbnail`을 조건부로 렌더링해야 합니다.

- **구조 예시:**

  ```python
  # pages/my_page.py
  from components.image_thumbnail import image_thumbnail
  from components.library.library_chooser_button import library_chooser_button

  @me.component
  def _uploader_placeholder(on_upload, on_open_library):
      with me.box(style=...): # 점선 테두리 스타일
          me.uploader(on_upload=on_upload, ...)
          library_chooser_button(on_library_select=on_open_library, ...)

  def my_page_content():
      state = me.state(PageState)
      if state.my_image_uri:
          image_thumbnail(
              image_uri=state.my_image_uri,
              on_remove=handle_remove_image,
              ...
          )
      else:
          _uploader_placeholder(
              on_upload=handle_upload,
              on_open_library=handle_open_library,
          )
  ```

### 분석 및 계측 (Analytics and Instrumentation)

새로운 기능을 추가할 때, `common/analytics.py`의 분석 프레임워크로 계측하여 사용자 행동과 애플리케이션 성능에 대한 통찰력을 제공하는 것이 중요합니다.

#### 페이지 조회 (Page Views)

페이지 조회 추적은 `page_scaffold` 컴포넌트에 의해 자동으로 처리됩니다. 새 페이지를 만들 때, 자동 페이지 조회 로깅을 활성화하려면 이 스캐폴드로 감싸야 합니다.

#### UI 상호 작용 (UI Interactions)

UI 상호 작용을 추적하는 두 가지 방법이 있습니다: 간단한 버튼 클릭을 위한 `@track_click` 데코레이터와 다른 컨트롤을 위한 `log_ui_click` 함수입니다.

##### 버튼 클릭

버튼 클릭을 추적하려면 이벤트 핸들러에 `@track_click` 데코레이터를 사용하세요. 이것은 버튼을 계측하는 가장 간단한 방법입니다.

**예시:**

```python
from common.analytics import track_click

@track_click(element_id="my_page_generate_button")
def on_generate_click(e: me.ClickEvent):
    # 이벤트 핸들러 로직
    yield
```

##### 기타 컨트롤

간단한 클릭 이벤트가 없는 UI 요소(예: 슬라이더, 선택, 텍스트 입력)의 경우, 이벤트 핸들러 내부에서 `log_ui_click` 함수를 직접 사용할 수 있습니다.

**예시:**

```python
from common.analytics import log_ui_click
from state.state import AppState

def on_slider_change(e: me.SliderValueChangeEvent):
    app_state = me.state(AppState)
    log_ui_click(
        element_id="my_page_slider",
        page_name=app_state.current_page,
        session_id=app_state.session_id,
        extras={"value": e.value},
    )
    # 이벤트 핸들러 로직
    yield
```

#### 요소 ID (Element IDs)

`element_id`를 선택할 때, 일관된 명명 규칙을 사용하세요. 좋은 관행은 `page_name_element_type_name` 형식을 사용하는 것입니다. 예를 들어:

- `imagen_generate_button`
- `veo_aspect_ratio_select`
- `chirp_text_input`

#### 모델 호출 (Model Calls)

생성 모델 호출의 성능과 상태를 추적하려면 `track_model_call` 컨텍스트 관리자를 사용하세요.

**예시:**

```python
from common.analytics import track_model_call

with track_model_call("my-generative-model-v1", prompt_length=len(prompt)):
    model.generate_content(...)
```

## 새 페이지 추가 방법

애플리케이션에 새 페이지를 추가하는 것은 페이지별 로직을 자체적으로 유지하는 간소화된 모듈식 패턴을 따릅니다.

### 1단계: 페이지 파일 생성

`pages/` 디렉토리에 새 Python 파일을 생성합니다 (예: `my_new_page.py`).

### 2단계: 페이지 구조 정의

새 파일 내에 페이지의 핵심 컴포넌트를 정의합니다. 일반적인 페이지 파일은 다음을 포함합니다:

1.  **State Class:** 페이지에 자체 상태가 있는 경우 `@me.stateclass`를 사용하여 상태 클래스를 정의합니다.
2.  **UI Content Function:** 페이지의 UI를 빌드하는 함수를 생성합니다 (예: `my_new_page_content()`).
3.  **Page Route Function:** `@me.page(...)`로 데코레이팅된 메인 페이지 진입점 함수(보통 `page()`로 명명)를 생성합니다.

**`pages/my_new_page.py`:**

```python
import mesop as me
from state.state import AppState
from components.header import header
from components.page_scaffold import page_frame, page_scaffold

@me.stateclass
class PageState:
    my_value: str = "안녕"

def my_new_page_content():
    state = me.state(PageState)
    with page_frame():
        header("내 새 페이지", "rocket_launch")
        me.text(f"새 페이지에 오신 것을 환영합니다! 내 값은: {state.my_value}")

@me.page(
    path="/my_new_page",
    title="내 새 페이지 - GenMedia Creative Studio",
)
def page():
    with page_scaffold(page_name="my_new_page"):
        my_new_page_content()
```

### 3단계: `main.py`에 페이지 등록

`main.py`에서 새 페이지 모듈을 가져와 검색 가능하게 만듭니다.

```python
from pages import my_new_page as my_new_page_page
```

### 4단계: 내비게이션에 페이지 추가

`config/navigation.json`에 새 페이지를 추가하여 UI에서 액세스할 수 있게 합니다.

```json
{
  "id": 60,
  "display": "내 새 페이지",
  "icon": "rocket_launch",
  "route": "/my_new_page",
  "group": "workflows"
}
```
