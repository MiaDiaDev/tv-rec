"""Redis caching utilities for German TV Recommender."""

import json
import redis
from functools import wraps
from typing import Any, Callable, Optional
from app.config import config


class CacheClient:
    """Redis cache client wrapper."""

    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                decode_responses=True
            )
            self.client.ping()
            self.enabled = True
        except (redis.ConnectionError, redis.RedisError) as e:
            print(f"Redis not available: {e}. Running without cache.")
            self.enabled = False
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled:
            return False
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False


# Global cache instance
cache_client = CacheClient()


def cached(ttl: int = 3600):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = cache_client.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache_client.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
