from sqlalchemy.orm import Session
import models, schemas, auth_utils
from uuid import UUID
from fastapi import HTTPException, status

# Organization Services
def create_organization(db: Session, org: schemas.OrganizationCreate):
    db_org = models.Organization(name=org.name)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_organization(db: Session, org_id: UUID):
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

# User Services
def create_user(db: Session, user: schemas.UserCreate, org_id: UUID):
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        organization_id=org_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Task Services
def create_task(db: Session, task: schemas.TaskCreate, org_id: UUID):
    db_task = models.Task(**task.model_dump(), organization_id=org_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, org_id: UUID, skip: int = 0, limit: int = 10, status: str = None, priority: str = None):
    query = db.query(models.Task).filter(models.Task.organization_id == org_id)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    return query.offset(skip).limit(limit).all()

def get_tasks_with_count(db: Session, org_id: UUID, skip: int = 0, limit: int = 10, status: str = None, priority: str = None):
    query = db.query(models.Task).filter(models.Task.organization_id == org_id)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    return tasks, total

def update_task(db: Session, task_id: UUID, task_update: schemas.TaskUpdate, org_id: UUID):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.organization_id == org_id).first()
    if not db_task:
        return None
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: UUID, org_id: UUID):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.organization_id == org_id).first()
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
