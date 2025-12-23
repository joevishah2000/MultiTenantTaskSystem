<<<<<<< HEAD
# MultiTenantTaskSystem
=======
# Multi-Tenant Task & Workflow Management System

This is a production-style backend system built with FastAPI, PostgreSQL, and Redis.

## Features
- **Multi-Tenancy**: Every company (organization) has isolated data.
- **Authentication**: JWT access and refresh tokens.
- **RBAC**: Admin and User roles with different permissions.
- **Caching**: Redis integration to speed up task listing.
- **Async Jobs**: Background tasks for non-critical logging and emails.
- **Pagination & Filtering**: Efficient data retrieval for tasks.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy (PostgreSQL), Redis.
- **Frontend**: Minimal React (Tailwind CSS).

## How to Run locally

### Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `uvicorn main:app --reload`
4. Visit `http://localhost:8000/docs` for interactive API documentation.

### Frontend
1. Navigate to `frontend/`
2. Open `index.html` in your browser.
3. Configure `API_URL` in `index.html` if your backend is running on a different port.

### Running Tests
1. Navigate to `backend/`
2. Run `pytest test_main.py`
>>>>>>> cc40a8a (Initial commit: backend + minimal frontend)
