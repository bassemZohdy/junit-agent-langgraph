import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Dict
from functools import wraps


T = TypeVar('T')


class FileCacheEntry:
    """Represents a cached file entry."""
    
    def __init__(self, content: Any, mtime: float):
        self.content = content
        self.mtime = mtime
        self.access_time = time.time()


class CacheManager:
    """
    Thread-safe cache manager with LRU eviction and TTL.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: Optional[int] = None
    ):
        self._cache: Dict[str, FileCacheEntry] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._access_order: list[str] = []
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            return None
        
        entry = self._cache[key]
        
        if self._ttl_seconds and (time.time() - entry.access_time) > self._ttl_seconds:
            self._remove(key)
            self._misses += 1
            return None
        
        entry.access_time = time.time()
        self._update_access_order(key)
        self._hits += 1
        
        return entry.content
    
    def put(self, key: str, value: Any) -> None:
        """
        Put value into cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if len(self._cache) >= self._max_size:
            self._evict_lru()
        
        self._cache[key] = FileCacheEntry(value, time.time())
        self._access_order.append(key)
    
    def invalidate(self, key: str) -> None:
        """
        Invalidate specific cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        self._remove(key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()
    
    def _remove(self, key: str) -> None:
        """Remove key from cache and access order."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._access_order:
            lru_key = self._access_order[0]
            self._remove(lru_key)
    
    def _update_access_order(self, key: str) -> None:
        """Update access order when key is accessed."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2%}",
            "total_requests": total_requests
        }


_global_cache: Optional[CacheManager] = None


def get_cache(max_size: int = 1000, ttl_seconds: Optional[int] = None) -> CacheManager:
    """
    Get or create global cache manager.
    
    Args:
        max_size: Maximum number of cache entries
        ttl_seconds: Time to live for cache entries (None = no expiration)
    
    Returns:
        CacheManager instance
    """
    global _global_cache
    
    if _global_cache is None:
        _global_cache = CacheManager(max_size, ttl_seconds)
    
    return _global_cache


def file_hash(file_path: str) -> str:
    """
    Generate hash for file path.
    
    Args:
        file_path: Path to file
    
    Returns:
        SHA256 hash of file path
    """
    return hashlib.sha256(file_path.encode()).hexdigest()


def cache_file_read(func: Callable[[str], T]) -> Callable[[str], T]:
    """
    Decorator to cache file read operations.
    
    Usage:
        @cache_file_read
        def read_file_content(file_path: str) -> str:
            ...
    """
    @wraps(func)
    def wrapper(file_path: str) -> T:
        cache = get_cache()
        key = f"file:{file_hash(file_path)}"
        
        if not Path(file_path).exists():
            cache.invalidate(key)
            return func(file_path)
        
        cached = cache.get(key)
        
        if cached is not None:
            mtime = os.path.getmtime(file_path)
            if hasattr(cached, 'mtime') and cached.mtime >= mtime:
                return cached.content
            else:
                cache.invalidate(key)
        
        result = func(file_path)
        cache.put(key, result)
        
        return result
    
    return wrapper


def cache_ast_parse(func: Callable[[str], T]) -> Callable[[str], T]:
    """
    Decorator to cache AST parsing operations.
    
    Usage:
        @cache_ast_parse
        def parse_java_file(content: str) -> AST:
            ...
    """
    @wraps(func)
    def wrapper(content: str) -> T:
        cache = get_cache()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        key = f"ast:{content_hash}"
        
        cached = cache.get(key)
        
        if cached is not None:
            return cached
        
        result = func(content)
        cache.put(key, result)
        
        return result
    
    return wrapper


def invalidate_file_cache(file_path: str) -> None:
    """
    Invalidate cache for a specific file.
    
    Args:
        file_path: Path to file
    """
    cache = get_cache()
    key = f"file:{file_hash(file_path)}"
    cache.invalidate(key)


def invalidate_all_cache() -> None:
    """Clear all cache."""
    cache = get_cache()
    cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get current cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    cache = get_cache()
    return cache.get_stats()
