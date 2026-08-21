# Phase 1: Project Setup & Architecture Baseline - Execution Plan

## Task Group 1: Backend Infrastructure Setup (Django + DRF)
- [x] **Task 1.1**: Create `backend/requirements.txt` containing dependencies: `django>=5.0`, `djangorestframework`, `django-cors-headers`, `python-dotenv`, `groq`, `pdfplumber`, `requests`.
- [x] **Task 1.2**: Create Python virtual environment under `backend/venv` and install `requirements.txt`.
- [x] **Task 1.3**: Initialize Django project `counterpoint` inside `backend/` and create `api` app (`python manage.py startapp api`).
- [x] **Task 1.4**: Configure `counterpoint/settings.py` to register `rest_framework`, `corsheaders`, `api`, and set up CORS allowed origins.
- [x] **Task 1.5**: Create health check view in `api/views.py` and route it to `/api/health/` returning HTTP 200 `{"status": "ok", "app": "counterpoint"}`.

## Task Group 2: Frontend Workspace Initialization (Vite + Vanilla CSS + Vitest)
- [x] **Task 2.1**: Initialize Vite frontend under `frontend/` directory.
- [x] **Task 2.2**: Configure `frontend/src/index.css` with core Vanilla CSS design tokens (theme variables, reset, font stacks, container layouts).
- [x] **Task 2.3**: Create baseline `index.html` structure with clean, responsive header and main content layout.
- [x] **Task 2.4**: Create basic client script `frontend/src/main.js` to verify frontend rendering.
- [x] **Task 2.5**: Configure Vitest runner script in `frontend/package.json` (`npm run test`) and create baseline test `frontend/src/api.test.js`.

## Task Group 3: Environment Configuration & Stack Verification
- [x] **Task 3.1**: Create `.env.example` in root / backend with template configuration keys.
- [x] **Task 3.2**: Execute `python manage.py check` to verify Django system settings without errors.
- [x] **Task 3.3**: Run Vite dev build (`npm run build`) in `frontend/` to confirm zero compilation errors.
- [x] **Task 3.4**: Test cross-origin fetch from frontend client to backend `/api/health/` endpoint.
- [x] **Task 3.5**: Execute Vitest unit test suite (`npm run test`) in `frontend/` to verify 100% test pass rate.
