import redis
import os
import json
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Redis connection error: {e}")
    redis_client = None

def get_cache(key: str):
    if not redis_client:
        return None
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_cache(key: str, value: any, ttl: int = 60):
    if not redis_client:
        return
    redis_client.setex(key, ttl, json.dumps(value))

def delete_cache(key: str):
    if not redis_client:
        return
    redis_client.delete(key)

def invalidate_org_cache(org_id: str):
    if not redis_client:
        return
    # Example: pattern-based invalidation (be careful with KEYS in production)
    keys = redis_client.keys(f"tasks:{org_id}:*")
    if keys:
        redis_client.delete(*keys)
