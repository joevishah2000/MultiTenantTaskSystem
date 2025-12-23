from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Organization Schemas
class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"
    organization_id: Optional[UUID] = None

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: UUID
    role: str
    organization_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
    org_id: Optional[str] = None

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    assigned_to: Optional[UUID] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None

class Task(TaskBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskPagination(BaseModel):
    tasks: List[Task]
    total: int
    page: int
    limit: int

# Stats Schema
class OrgStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
