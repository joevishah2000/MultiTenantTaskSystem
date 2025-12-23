from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, services, auth_utils, dependencies, database, cache, background_tasks
from database import engine, get_db
from dependencies import get_current_user, require_admin
import uuid

# Initialize DB
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Tenant Task API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Routes
@app.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db), bg_tasks: BackgroundTasks = BackgroundTasks()):
    # 1. Create Organization if not exists or if registering first user
    # Simplified: Every new registration creates a new org for this demo
    org = services.create_organization(db, schemas.OrganizationCreate(name=f"{user.email}'s Org"))
    db_user = services.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # First user is admin
    user.role = "admin"
    new_user = services.create_user(db, user, org.id)
    
    bg_tasks.add_task(background_tasks.send_welcome_email, user.email)
    bg_tasks.add_task(background_tasks.log_audit_event, str(new_user.id), "register", "user")
    
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = services.get_user_by_email(db, email=user_credentials.email)
    if not user or not auth_utils.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_utils.create_access_token(
        data={"sub": str(user.id), "org_id": str(user.organization_id), "role": user.role}
    )
    refresh_token = auth_utils.create_refresh_token(
        data={"sub": str(user.id)}
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# Task Routes
@app.get("/tasks", response_model=schemas.TaskPagination)
def read_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    cache_key = f"tasks:{current_user.organization_id}:{current_user.id}:{status}:{priority}:{page}:{limit}"
    cached_data = cache.get_cache(cache_key)
    if cached_data:
        return cached_data

    skip = (page - 1) * limit
    tasks, total = services.get_tasks_with_count(db, current_user.organization_id, skip=skip, limit=limit, status=status, priority=priority)
    
    response_data = {
        "tasks": tasks,
        "total": total,
        "page": page,
        "limit": limit
    }
    
    # Store in cache
    cache.set_cache(cache_key, jsonable_encoder(response_data), ttl=60)
    
    return response_data

@app.post("/tasks", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user),
    bg_tasks: BackgroundTasks = BackgroundTasks()
):
    new_task = services.create_task(db, task, current_user.organization_id)
    cache.invalidate_org_cache(str(current_user.organization_id))
    bg_tasks.add_task(background_tasks.log_audit_event, str(current_user.id), "create", "task", str(new_task.id))
    return new_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: uuid.UUID, 
    task_update: schemas.TaskUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    updated_task = services.update_task(db, task_id, task_update, current_user.organization_id)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    cache.invalidate_org_cache(str(current_user.organization_id))
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: uuid.UUID, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    success = services.delete_task(db, task_id, current_user.organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    cache.invalidate_org_cache(str(current_user.organization_id))
    return {"detail": "Task deleted"}

# Admin Routes
@app.get("/admin/stats", response_model=schemas.OrgStats)
def get_org_stats(
    db: Session = Depends(get_db), 
    admin_user: models.User = Depends(require_admin)
):
    total = db.query(models.Task).filter(models.Task.organization_id == admin_user.organization_id).count()
    pending = db.query(models.Task).filter(models.Task.organization_id == admin_user.organization_id, models.Task.status == "pending").count()
    completed = db.query(models.Task).filter(models.Task.organization_id == admin_user.organization_id, models.Task.status == "completed").count()
    
    return {
        "total_tasks": total,
        "pending_tasks": pending,
        "completed_tasks": completed
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
