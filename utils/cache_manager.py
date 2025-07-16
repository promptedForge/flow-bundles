"""
Memory caching system for Skyward Assistable Bundle

Provides efficient caching for API responses, computed results, and frequently
accessed data to improve performance and reduce API calls.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from collections import OrderedDict
import threading
from functools import wraps
import pickle

class CacheEntry:
    """Represents a single cache entry"""
    
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None,
                 tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.expires_at = self.created_at + ttl if ttl else None
        self.tags = tags or []
        self.metadata = metadata or {}
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def access(self) -> Any:
        """Access the cached value and update access statistics"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value
    
    def get_age(self) -> float:
        """Get age of cache entry in seconds"""
        return time.time() - self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary for serialization"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "ttl": self.ttl,
            "expires_at": self.expires_at,
            "tags": self.tags,
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }

class CacheManager:
    """Thread-safe memory cache manager with TTL, LRU eviction, and tagging"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.tag_index: Dict[str, List[str]] = {}  # tag -> list of keys
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create a deterministic key from args and kwargs
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self.stats["misses"] += 1
                self.stats["expirations"] += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            
            return entry.access()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None,
           tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Set value in cache"""
        with self.lock:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Remove existing entry if present
            if key in self.cache:
                self._remove_entry(key)
            
            # Check size limit and evict if necessary
            while len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Create and store entry
            entry = CacheEntry(key, value, ttl, tags, metadata)
            self.cache[key] = entry
            
            # Update tag index
            if tags:
                for tag in tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = []
                    self.tag_index[tag].append(key)
    
    def delete(self, key: str) -> bool:
        """Delete specific key from cache"""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def _remove_entry(self, key: str):
        """Remove entry and update indexes"""
        if key in self.cache:
            entry = self.cache[key]
            del self.cache[key]
            
            # Update tag index
            for tag in entry.tags:
                if tag in self.tag_index and key in self.tag_index[tag]:
                    self.tag_index[tag].remove(key)
                    if not self.tag_index[tag]:
                        del self.tag_index[tag]
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self.cache:
            lru_key = next(iter(self.cache))
            self._remove_entry(lru_key)
            self.stats["evictions"] += 1
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with specific tag"""
        with self.lock:
            if tag not in self.tag_index:
                return 0
            
            keys_to_remove = self.tag_index[tag].copy()
            for key in keys_to_remove:
                self._remove_entry(key)
            
            return len(keys_to_remove)
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        with self.lock:
            import re
            regex = re.compile(pattern)
            
            keys_to_remove = [key for key in self.cache.keys() if regex.search(key)]
            for key in keys_to_remove:
                self._remove_entry(key)
            
            return len(keys_to_remove)
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.tag_index.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        with self.lock:
            expired_keys = []
            
            for key, entry in self.cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
                self.stats["expirations"] += 1
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": hit_rate,
                "evictions": self.stats["evictions"],
                "expirations": self.stats["expirations"],
                "tags": len(self.tag_index)
            }
    
    def get_entries_info(self) -> List[Dict[str, Any]]:
        """Get information about cache entries"""
        with self.lock:
            entries_info = []
            
            for entry in self.cache.values():
                info = {
                    "key": entry.key,
                    "age_seconds": entry.get_age(),
                    "ttl": entry.ttl,
                    "expires_at": entry.expires_at,
                    "access_count": entry.access_count,
                    "last_accessed": entry.last_accessed,
                    "tags": entry.tags,
                    "is_expired": entry.is_expired()
                }
                entries_info.append(info)
            
            return entries_info

class APIResponseCache(CacheManager):
    """Specialized cache for API responses"""
    
    def __init__(self, max_size: int = 500, default_ttl: int = 1800):  # 30 minutes default
        super().__init__(max_size, default_ttl)
        self.api_specific_ttls = {
            "assistable_assistants": 3600,  # 1 hour
            "ghl_contacts": 1800,           # 30 minutes
            "ghl_conversations": 300,       # 5 minutes
            "assistable_conversations": 600  # 10 minutes
        }
    
    def cache_api_response(self, service: str, operation: str, params: Dict[str, Any],
                          response: Any) -> str:
        """Cache API response with service-specific TTL"""
        
        # Generate cache key
        key_data = {
            "service": service,
            "operation": operation,
            "params": params
        }
        cache_key = self._generate_key(key_data)
        
        # Determine TTL
        api_key = f"{service}_{operation}"
        ttl = self.api_specific_ttls.get(api_key, self.default_ttl)
        
        # Set tags
        tags = [service, operation, f"{service}_{operation}"]
        
        # Add metadata
        metadata = {
            "service": service,
            "operation": operation,
            "params_hash": hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        }
        
        self.set(cache_key, response, ttl=ttl, tags=tags, metadata=metadata)
        
        return cache_key
    
    def get_api_response(self, service: str, operation: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached API response"""
        
        key_data = {
            "service": service,
            "operation": operation,
            "params": params
        }
        cache_key = self._generate_key(key_data)
        
        return self.get(cache_key)

class ComputationCache(CacheManager):
    """Specialized cache for computed results"""
    
    def __init__(self, max_size: int = 200, default_ttl: int = 7200):  # 2 hours default
        super().__init__(max_size, default_ttl)

def cached(ttl: Optional[int] = None, 
          tags: Optional[List[str]] = None,
          cache_instance: Optional[CacheManager] = None):
    """Decorator for caching function results"""
    
    def decorator(func: Callable) -> Callable:
        # Use global cache if none provided
        cache = cache_instance or global_cache
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__module__}.{func.__name__}_{cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Cache result
            func_tags = tags or [func.__name__, func.__module__]
            cache.set(cache_key, result, ttl=ttl, tags=func_tags)
            
            return result
        
        # Add cache management methods to function
        wrapper.cache_clear = lambda: cache.invalidate_by_tag(func.__name__)
        wrapper.cache_info = lambda: cache.get_stats()
        
        return wrapper
    
    return decorator

def cache_key_from_request(service: str, operation: str, **params) -> str:
    """Generate cache key for API requests"""
    key_data = {
        "service": service,
        "operation": operation,
        "params": params
    }
    return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

class DistributedCacheManager:
    """Mock distributed cache interface for future Redis integration"""
    
    def __init__(self, local_cache: CacheManager):
        self.local_cache = local_cache
        self.redis_client = None  # Would be Redis client in production
    
    def get(self, key: str) -> Optional[Any]:
        """Get from local cache first, then distributed cache"""
        # Try local cache first
        value = self.local_cache.get(key)
        if value is not None:
            return value
        
        # TODO: Try Redis cache
        # if self.redis_client:
        #     value = self.redis_client.get(key)
        #     if value:
        #         # Store in local cache
        #         self.local_cache.set(key, value)
        #         return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set in both local and distributed cache"""
        # Set in local cache
        self.local_cache.set(key, value, ttl=ttl)
        
        # TODO: Set in Redis
        # if self.redis_client:
        #     self.redis_client.setex(key, ttl or 3600, pickle.dumps(value))

# Global cache instances
global_cache = CacheManager(max_size=1000, default_ttl=3600)
api_cache = APIResponseCache()
computation_cache = ComputationCache()

# Cache warmup functions
def warmup_cache():
    """Warm up cache with common data"""
    # This would be called on startup to pre-populate cache
    pass

def setup_cache_cleanup():
    """Setup periodic cache cleanup"""
    import threading
    import time
    
    def cleanup_worker():
        while True:
            time.sleep(300)  # Clean up every 5 minutes
            global_cache.cleanup_expired()
            api_cache.cleanup_expired()
            computation_cache.cleanup_expired()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

# Start cleanup on import
setup_cache_cleanup()
