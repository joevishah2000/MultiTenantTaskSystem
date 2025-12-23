import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
print(f"Testing connection to: {REDIS_URL.split('@')[-1]}") # Hide password

try:
    # Try current configuration
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    print("SUCCESS: Connected with current settings!")
except Exception as e:
    print(f"ERROR: Current settings failed: {e}")

print("-" * 20)

# Try forcing SSL if not present
if "rediss://" not in REDIS_URL:
    SSL_URL = REDIS_URL.replace("redis://", "rediss://")
    print(f"Testing connection with SSL (rediss://)...")
    try:
        r_ssl = redis.from_url(SSL_URL, decode_responses=True)
        r_ssl.ping()
        print("SUCCESS: Connected with SSL!")
    except Exception as e:
        print(f"ERROR: SSL settings failed: {e}")
