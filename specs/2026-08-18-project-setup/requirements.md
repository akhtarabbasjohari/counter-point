# Phase 1: Project Setup & Architecture Baseline - Requirements

## 1. Context & Purpose
This spec covers Phase 1 of the [CounterPoint Implementation Roadmap](../roadmap.md). The objective is to set up a clean, full dual-stack repository foundation comprising a **Django 5.x + Django REST Framework (DRF)** backend API and a **Vite + Vanilla CSS** frontend web application.

## 2. Scope of Work
- **Backend Setup**:
  - Python 3.11+ environment configuration (`requirements.txt`).
  - Django project initialization (`counterpoint`) with a dedicated app (`api`).
  - Integration of `django-cors-headers` to enable local cross-origin API calls from the Vite client.
  - Baseline health check API endpoint (`/api/health/`).
- **Frontend Setup**:
  - Vite development workspace initialized under `frontend/`.
  - Base design system setup in `index.css` using Vanilla CSS design tokens (typography, color palette, flex/grid layout rules).
- **Environment Configuration**:
  - Structured `.env.example` documenting runtime keys (`GROQ_API_KEY`, `SECRET_KEY`, `DEBUG`, `CORS_ALLOWED_ORIGINS`).

## 3. Key Decisions & Constraints
- **Framework Choices**: Django 5.x + DRF for backend scalability and Python AI ecosystem access; Vite + Vanilla CSS for lightweight, fast frontend rendering without heavy CSS framework dependencies.
- **Project Structure**:
  ```text
  counter-point/
  ├── backend/               # Django + DRF backend
  │   ├── manage.py
  │   ├── requirements.txt
  │   ├── counterpoint/      # Project settings & URL routing
  │   └── api/               # API app, views, serializers
  ├── frontend/              # Vite + Vanilla CSS frontend
  │   ├── package.json
  │   ├── index.html
  │   └── src/
  └── specs/                 # Specifications & Feature documentation
  ```
- **CORS Policy**: Allow `http://localhost:5173` (Vite default dev port) in development.

## 4. Alignment with Core Specs
- Aligns directly with [specs/mission.md](../mission.md) by laying the groundwork for fast, transparent competitive research tools.
- Adheres strictly to [specs/tech-stack.md](../tech-stack.md) technology selections (Python/Django backend + Vite/Vanilla CSS frontend).
