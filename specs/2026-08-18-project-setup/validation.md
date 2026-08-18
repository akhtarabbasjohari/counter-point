# Phase 1: Project Setup & Architecture Baseline - Validation Criteria

To verify that Phase 1 implementation is successful and ready to be merged into `main`, all of the following validation checks must pass:

## 1. Backend Verification Checks
- [ ] **Django System Check**: Running `python manage.py check` inside `backend/` completes with 0 errors.
- [ ] **Database Migration Check**: Running `python manage.py migrate` applies initial Django migrations cleanly.
- [ ] **Health Endpoint Check**: `GET http://localhost:8000/api/health/` returns HTTP status `200 OK` with JSON response:
  ```json
  {
    "status": "ok",
    "app": "counterpoint"
  }
  ```

## 2. Frontend Verification Checks
- [ ] **Vite Dev Server Check**: Running `npm run dev` inside `frontend/` launches development server without errors on port `5173`.
- [ ] **Vite Production Build Check**: Running `npm run build` inside `frontend/` generates production bundle in `frontend/dist/` without compilation warnings or errors.

## 3. Integration & CORS Verification
- [ ] **Cross-Origin API Call**: Fetching `/api/health/` from `http://localhost:5173` via browser/JavaScript client returns HTTP 200 without CORS header blocking errors.
- [ ] **Environment Template**: `.env.example` exists and contains placeholder configuration keys (`SECRET_KEY`, `DEBUG`, `GROQ_API_KEY`, `CORS_ALLOWED_ORIGINS`).

## 4. Documentation & Git Cleanliness
- [ ] Working tree clean, with all new files properly added to git under `backend/`, `frontend/`, and `specs/`.
