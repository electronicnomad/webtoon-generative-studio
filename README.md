[English](#english) | [한국어](#korean)

<a id="english"></a>

# Webtoon Generator

A specialized AI-powered workstation for webtoon and comic creators, built on Google Cloud's generative media platform.

> ###### _Thank you for your interest. Please note that this is not an officially supported Google product. This project is not recommended for use in a production environment._

![Webtoon Generator](./assets/home_screen.png)

## Webtoon Production Pipeline

Webtoon Generator provides a streamlined workflow for professional and amateur creators:

1.  **Banana Studio (Ideation):** Ultra-fast concept exploration using Gemini 2.5 Flash (Nano Banana).
2.  **Storyboard (Planning):** Generate scripts and visual storyboards from simple prompts.
3.  **Cartoon Pro (Rendering):** Turn your hand-drawn sketches (conti) into high-quality webtoon cuts. Uses "Red Color Recognition" to follow your specific artistic instructions.
4.  **Character Consistency:** Ensure your protagonist looks the same in every frame, regardless of angle or pose.
5.  **Asset Library:** A central hub to manage your character sheets, background assets, and final panels.

## Features

- **Gemini 2.5 Flash (Nano Banana):** Real-time image generation for instant feedback.
- **Imagen 3 & 4:** High-fidelity rendering for cover art and key panels.
- **Sketch-to-Webtoon:** Advanced AI that understands your rough sketches.
- **Multi-user Support:** Collaborate with your team across different domains.

## Getting Started

### Prerequisites
- [uv](https://github.com/astral-sh/uv) package manager.
- Google Cloud Project with necessary APIs enabled.

### Running Locally
```bash
uv sync
uv run main.py
```

### Deployment
Refer to [DEPLOY.md](DEPLOY.md) for Terraform-based deployment to Cloud Run.

---

<a id="korean"></a>

# Webtoon Generator

Google Cloud의 생성형 미디어 플랫폼을 기반으로 구축된 **웹툰 및 만화 제작자를 위한 전문 AI 워크스테이션**입니다.

> ###### _방문해 주셔서 감사합니다. 본 프로젝트는 Google의 공식 제품이 아님을 알려드립니다. 실험 및 데모 목적으로 제작되었으므로, 프로덕션 환경에서의 사용은 권장하지 않습니다._

## 웹툰 제작 파이프라인

Webtoon Generator는 작가들을 위해 최적화된 제작 흐름을 제공합니다.

1.  **바나나 스튜디오 (아이디어):** Gemini 2.5 Flash(Nano Banana)를 사용한 초고속 컨셉 탐색.
2.  **스토리보드 (기획):** 간단한 프롬프트로 시나리오와 비주얼 스토리보드 생성.
3.  **카툰 프로 (본 작업):** 직접 그린 콘티(스케치)를 고품질 웹툰 컷으로 변환. "적색 인식 기능"을 통해 작가의 연출 의도를 정확히 반영합니다.
4.  **캐릭터 일관성 유지:** 어떤 각도나 포즈에서도 주인공의 외형을 동일하게 유지.
5.  **자산 라이브러리:** 캐릭터 시트, 배경 자산, 최종 원고를 한곳에서 관리하는 중앙 허브.

## 주요 기능

- **Gemini 2.5 Flash (Nano Banana):** 실시간 이미지 생성을 통한 즉각적인 피드백.
- **Imagen 3 & 4:** 표지 및 주요 컷을 위한 고해상도 렌더링.
- **콘티 기반 생성:** 러프한 스케치를 이해하고 완성해 주는 고급 AI 기능.
- **다중 사용자 지원:** 서로 다른 도메인의 팀원들과 협업 가능.

## 시작하기

### 사전 준비
- [uv](https://github.com/astral-sh/uv) 패키지 매니저.
- 필요한 API가 활성화된 Google Cloud 프로젝트.

### 로컬 실행
```bash
uv sync
uv run main.py
```

### 배포
Cloud Run 배포를 위한 자세한 지침은 [DEPLOY.md](DEPLOY.md)를 참조하세요.
