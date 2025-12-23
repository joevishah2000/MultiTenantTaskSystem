# Multi-Tenant Task & Workflow Management System

This is a production-style backend system built with FastAPI, PostgreSQL, and Redis, featuring a modern, responsive React frontend.

## Features
- **Multi-Tenancy**: Every company (organization) has isolated data.
- **Authentication**: JWT access and refresh tokens.
- **RBAC**: Admin and User roles with different permissions.
- **Caching**: Redis integration to speed up task listing (with fault tolerance).
- **Async Jobs**: Background tasks for non-critical logging and emails.
- **Pagination & Filtering**: 
    - Numbered pagination (10 items per page).
    - Filter tasks by Status (Pending, Ongoing, Done) and Priority (Low, Medium, High).
- **Modern UI**: 
    - Clean, square-structured aesthetic.
    - Glassmorphism effects with simplified geometry.
    - Responsive dashboard with statistics.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy (PostgreSQL), Redis.
- **Frontend**: React (Vite), Tailwind CSS, Framer Motion, Lucide Icons.

## How to Run locally

### Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `uvicorn main:app --reload`
4. Visit `http://localhost:8000/docs` for interactive API documentation.
   
   *Note: Ensure you have PostgreSQL and Redis running correctly. Update `.env` with your credentials.*

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run the dev server: `npm run dev`
4. Visit `http://localhost:5173` (or the port shown in terminal).

### Running Tests
1. Navigate to `backend/`
2. Run `pytest test_main.py`

### PostgreSQL (Supabase)
The project uses managed PostgreSQL via Supabase. Database schema is created and versioned using SQLAlchemy models and migrations.

![PostgreSQL (Supabase)](Screenshots\Redis_1.JPG)

### Redis Cache
Redis is used to cache high-read APIs such as task listings and user profile data, with TTL-based invalidation.

![Redis](Screenshots\Redis_1.JPG)

