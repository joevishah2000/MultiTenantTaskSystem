import time

def send_welcome_email(email: str):
    print(f"Sending welcome email to {email}...")
    time.sleep(2)  # Simulate network delay
    print(f"Email sent to {email}")

def log_audit_event(user_id: str, action: str, entity: str, details: str = None):
    print(f"Audit Log: User {user_id} performed {action} on {entity}. Details: {details}")
    # In a real app, you'd save this to the audit_logs table here too, 
    # but we'll do it via the service layer or background task.
