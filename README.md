# Landmine Soft College Student Portal (Assignment 2)

## Tech Stack (chosen)
- Backend: Django REST Framework
- Database: PostgreSQL (Render) / SQLite (local fallback)
- Auth: JWT (24h expiry) + role-based access (STUDENT / FACULTY / Admin roles)
- Swagger/OpenAPI: drf-spectacular

## Folder Structure
- `backend/` - Django + DRF APIs
- `frontend/` - React demo UI (scaffold in progress)
- `postman/` - Postman collection + environment

## Backend Setup (local)

1. Create env vars (optional for local sqlite)
   - Copy `backend/.env.example` to `backend/.env` (or export env vars in your shell)

2. Install dependencies
   - `cd backend`
   - `../backend/venv/bin/pip install -r requirements.txt` (if you recreated the venv)

3. Run migrations
   - `./venv/bin/python manage.py makemigrations`
   - `./venv/bin/python manage.py migrate`

4. Start server
   - `./venv/bin/python manage.py runserver`

Swagger UI:
- `http://localhost:8000/api/docs/`

## Tests
- `cd backend`
- `./venv/bin/pytest`

## Environment Variables

Required for PostgreSQL deployment (Render):
- `DJANGO_SECRET_KEY`
- `JWT_SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Optional:
- `DJANGO_DEBUG=true/false`
- `ALLOWED_HOSTS=*`

## Render Deployment (backend)
This repo includes `render.yaml`.

1. Create a Render “Web Service” for the backend.
2. Add environment variables listed above.
3. Point the service to `render.yaml` settings:
   - start command uses gunicorn: `gunicorn lms_portal.wsgi:application`

