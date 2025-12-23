from schemas import Task
import uuid
from datetime import datetime
import json

# Create a sample task object (simulating DB object)
class MockTaskDB:
    def __init__(self):
        self.id = uuid.uuid4()
        self.title = "Test Task"
        self.description = "Test Desc"
        self.status = "pending"
        self.priority = "medium"
        self.assigned_to = uuid.uuid4()
        self.organization_id = uuid.uuid4()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

task_db = MockTaskDB()

print(f"Testing serialization for Task ID: {task_db.id}")

try:
    # Simulate the line in main.py
    # data = Task.model_validate(task_db).model_dump() # This fails with json.dumps
    data = Task.model_validate(task_db).model_dump(mode='json')
    
    # Simulate Redis/Use json.dumps
    json_string = json.dumps(data)
    print("SUCCESS: Serialized to JSON:")
    print(json_string)
    
except Exception as e:
    print(f"ERROR: Serialization failed: {e}")
