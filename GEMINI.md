# GEMINI.md - Webtoon Generator

This project is a specialized fork of Vertex AI Creative Studio, re-engineered as **Webtoon Generator**. It focuses exclusively on providing an all-in-one AI-powered pipeline for webtoon and comic creation.

## Project Overview

-   **Core Focus:** End-to-end webtoon production (Scripting -> Storyboarding -> Character Design -> Final Rendering).
-   **Main Technologies:** Python 3.13, [Mesop](https://mesop-dev.github.io/mesop/), [FastAPI](https://fastapi.tiangolo.com/), Google Cloud Platform.
-   **Webtoon Pipeline:**
    -   **Banana Studio:** Ultra-fast ideation and asset generation using Nano Banana (Gemini 2.5 Flash).
    -   **Storyboard & Storyboard Pro:** Scripting and visual planning for scenes.
    -   **Cartoon & Cartoon Pro:** Sketch-to-webtoon rendering with instruction (Red color) recognition.
    -   **Character Consistency:** Maintaining character traits across different scenes and angles.
    -   **Library:** Central hub for managing sketches, character sheets, and generated assets.

## Architecture & Organization

-   **Active Pages (`pages/`):** Only webtoon-related pages are active and imported in `main.py`.
-   **State Management:** Page-specific states are co-located with their respective pages; global session data is in `state/state.py`.

## Building and Running

### Prerequisites
-   [uv](https://github.com/astral-sh/uv) package manager.
-   Google Cloud Project with Vertex AI and Firestore enabled.

## Authentication & Security

-   **IAP Managed:** Access is controlled via Identity-Aware Proxy.
-   **Granularity:** Supports both **Individual User** (email) and **Domain-wide** access.
-   **Multi-domain:** Can support multiple organizations, provided the OAuth Consent Screen is set to **External**.
-   **Roles:** Requires `roles/iap.httpsResourceAccessor` for authorized access.

### Local Development
1.  **Install:** `uv sync`
2.  **Config:** Set `PROJECT_ID` in `.env`.
3.  **Run:** `uv run main.py` (accessible at `http://localhost:8080`).

## Development Conventions

-   **Webtoon Focus:** Every new feature should align with the webtoon production pipeline.
-   **Library Integration:** New generation tools MUST integrate with the Library for asset reuse.
-   **Consistent UI:** Use `page_scaffold` for all new pages to maintain navigation and analytics.

## Code Quality
-   Linting: `ruff check .`
-   Formatting: `black .`
-   Tests: `pytest`
