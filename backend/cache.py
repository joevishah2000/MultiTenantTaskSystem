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
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Redis get error: {e}")
        return None

def set_cache(key: str, value: any, ttl: int = 60):
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"Redis set error: {e}")

def delete_cache(key: str):
    if not redis_client:
        return
    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"Redis delete error: {e}")

def invalidate_org_cache(org_id: str):
    if not redis_client:
        return
    try:
        # Example: pattern-based invalidation (be careful with KEYS in production)
        keys = redis_client.keys(f"tasks:{org_id}:*")
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Redis invalidate error: {e}")
