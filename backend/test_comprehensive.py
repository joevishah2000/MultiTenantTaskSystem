import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import uuid

# Use SQLite for testing logic (avoids network DB issues)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_comprehensive.db"
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

# Mock Redis Cache
from unittest.mock import MagicMock
import cache

cache.get_cache = MagicMock(return_value=None)
cache.set_cache = MagicMock()
cache.invalidate_org_cache = MagicMock()

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_full_flow():
    # 1. Register User
    email = "fullflow@example.com"
    password = "password123"
    reg_response = client.post("/auth/register", json={"email": email, "password": password})
    assert reg_response.status_code == 200
    user_id = reg_response.json()["id"]

    # 2. Login
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Task
    task_response = client.post("/tasks", json={"title": "My Task", "priority": "high"}, headers=headers)
    assert task_response.status_code == 200
    task_data = task_response.json()
    task_id = task_data["id"]
    assert task_data["title"] == "My Task"
    assert task_data["priority"] == "high"

    # 4. List Tasks
    list_response = client.get("/tasks", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    # 5. Update Task
    update_response = client.put(f"/tasks/{task_id}", json={"status": "in_progress"}, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"

    # 6. Admin Stats (User is admin by default in this demo logic)
    stats_response = client.get("/admin/stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_tasks"] == 1
    assert stats["pending_tasks"] == 0 # Updated to in_progress
    # Note: Logic in main.py counts "pending" and "completed", assuming others aren't counted in those specific buckets?
    # Let's check main.py logic: 
    # pending = ... .filter(..., status == "pending")
    # completed = ... .filter(..., status == "completed")
    # So "in_progress" won't show in those two, but will be in 'total'.
    
    # 7. Delete Task
    del_response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert del_response.status_code == 200

    # 8. Verify Delete
    list_response_after = client.get("/tasks", headers=headers)
    assert len(list_response_after.json()) == 0
