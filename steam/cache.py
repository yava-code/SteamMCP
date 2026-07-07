"""
TTL Cache for Steam API responses.

This module provides a simple in-memory cache with TTL (time-to-live) support
for caching Steam API responses, particularly useful for:
- Store data that doesn't change frequently
- Discovery data (featured items, specials, etc.)
- App details that are relatively static
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry:
    """A single cache entry with TTL."""
    value: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return time.time() > self.expires_at
    
    def ttl_remaining(self) -> float:
        """Get remaining TTL in seconds."""
        return max(0, self.expires_at - time.time())


class TTLCache:
    """
    Thread-safe TTL cache for Steam API responses.
    
    Features:
    - Configurable default TTL
    - Per-key TTL override
    - Automatic expiration
    - Thread-safe operations
    - Size limit with LRU eviction
    - Cache statistics
    
    Usage:
        cache = TTLCache(default_ttl=300, max_size=1000)
        
        # Cache a value
        cache.set("key", "value")
        
        # Get a value
        value = cache.get("key")
        
        # Get with default
        value = cache.get("missing_key", default="fallback")
        
        # Cache with custom TTL
        cache.set("key", "value", ttl=60)
        
        # Decorator usage
        @cache.cached(ttl=300)
        def expensive_function(arg1, arg2):
            return compute_expensive_result(arg1, arg2)
    """
    
    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000):
        """
        Initialize the TTL cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
            max_size: Maximum number of entries (0 for unlimited)
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        logger.info(f"TTLCache initialized with default_ttl={default_ttl}s, max_size={max_size}")
    
    def _generate_key(self, key: str) -> str:
        """Generate a consistent cache key."""
        return key
    
    def _evict_if_needed(self) -> None:
        """Evict entries if cache is full (LRU-style)."""
        if self.max_size <= 0:
            return
        
        while len(self._cache) >= self.max_size:
            # Find the oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]
            self._evictions += 1
            logger.debug(f"Cache evicted entry: {oldest_key}")
    
    def _cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        with self._lock:
            # Periodic cleanup
            if len(self._cache) > 0 and len(self._cache) % 100 == 0:
                self._cleanup_expired()
            
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return default
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return default
            
            self._hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            # Evict if needed
            self._evict_if_needed()
            
            effective_ttl = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + effective_ttl
            
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=expires_at,
                created_at=time.time()
            )
            logger.debug(f"Cache set: {key} (TTL: {effective_ttl}s)")
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> int:
        """
        Clear all entries from the cache.
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def invalidate(self, prefix: str) -> int:
        """
        Invalidate all entries with a given prefix.
        
        Args:
            prefix: Key prefix to match
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                del self._cache[key]
            return len(keys_to_remove)
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
                "evictions": self._evictions,
                "default_ttl": self.default_ttl
            }
    
    def cached(self, ttl: Optional[float] = None, key_prefix: str = ""):
        """
        Decorator to cache function results.
        
        Args:
            ttl: Time-to-live in seconds (uses default if None)
            key_prefix: Prefix for cache keys
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args, **kwargs) -> T:
                # Generate cache key from function name and arguments
                key_data = f"{key_prefix}:{func.__name__}:{args}:{frozenset(kwargs.items())}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl=ttl)
                logger.debug(f"Cache miss for {func.__name__}, cached result")
                return result
            
            # Preserve function metadata
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            wrapper.__wrapped__ = func
            
            return wrapper
        
        return decorator


# Global cache instances for different use cases
store_cache = TTLCache(default_ttl=300, max_size=1000)  # 5 minutes for store data
discovery_cache = TTLCache(default_ttl=600, max_size=500)  # 10 minutes for discovery data
app_cache = TTLCache(default_ttl=1800, max_size=2000)  # 30 minutes for app details
