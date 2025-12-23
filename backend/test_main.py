import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import os

# Use a separate test database or just memory for simple tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_and_login():
    # Register
    reg_response = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert reg_response.status_code == 200
    assert reg_response.json()["email"] == "test@example.com"

    # Login
    login_response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_create_task():
    # Login to get token
    client.post("/auth/register", json={"email": "task@example.com", "password": "password123"})
    login_response = client.post("/auth/login", json={"email": "task@example.com", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create Task
    headers = {"Authorization": f"Bearer {token}"}
    task_response = client.post("/tasks", json={"title": "Test Task"}, headers=headers)
    assert task_response.status_code == 200
    assert task_response.json()["title"] == "Test Task"

    # List Tasks
    list_response = client.get("/tasks", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
