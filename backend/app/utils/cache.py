from typing import Any, Optional, TypeVar, Callable
from functools import wraps
import json
from datetime import datetime, timedelta
import redis
from app.core.config import settings
from app.core.exceptions import FigmaCacheError

T = TypeVar('T')

class FigmaCache:
    """Cache manager for Figma data."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        except Exception as e:
            raise FigmaCacheError(f"Failed to connect to Redis: {str(e)}")

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            return self.redis.get(key)
        except Exception as e:
            raise FigmaCacheError(f"Failed to get from cache: {str(e)}")

    def set(self, key: str, value: str, expire_seconds: int = 3600) -> None:
        """Set value in cache with expiration."""
        try:
            self.redis.set(key, value, ex=expire_seconds)
        except Exception as e:
            raise FigmaCacheError(f"Failed to set in cache: {str(e)}")

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            self.redis.delete(key)
        except Exception as e:
            raise FigmaCacheError(f"Failed to delete from cache: {str(e)}")

def cache_figma_data(expire_seconds: int = 3600):
    """Decorator for caching Figma API responses."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Generate a simpler cache key using only serializable arguments
            cache_key_parts = [func.__name__]
            
            # Add non-self arguments to the key
            if args and len(args) > 1:  # Skip self argument
                cache_key_parts.extend(str(arg) for arg in args[1:])
            
            # Add kwargs to the key
            for key, value in sorted(kwargs.items()):
                if isinstance(value, (str, int, float, bool)):
                    cache_key_parts.append(f"{key}:{value}")
            
            cache_key = f"figma:{'_'.join(cache_key_parts)}"
            
            cache = FigmaCache()
            try:
                # Try to get from cache
                cached_data = cache.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
                
                # If not in cache, call function and cache result
                result = func(*args, **kwargs)
                if result:
                    try:
                        cache.set(cache_key, json.dumps(result), expire_seconds)
                    except (TypeError, ValueError):
                        # If result is not JSON serializable, skip caching
                        pass
                return result
            except FigmaCacheError:
                # If caching fails, just execute the function
                return func(*args, **kwargs)
        
        return wrapper
    return decorator 