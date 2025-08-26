"""
Simple in-memory cache for job discovery operations.
In production, this should be replaced with Redis or similar persistent cache.
"""

import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from threading import Lock

@dataclass
class CacheEntry:
    data: Any
    timestamp: float
    ttl: int  # Time to live in seconds

class JobDiscoveryCache:
    """Thread-safe in-memory cache for job discovery operations"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate a cache key from data"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, prefix: str, key_data: Any, default_ttl: int = 3600) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._generate_key(prefix, key_data)
        
        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                
                # Check if entry is expired
                if time.time() - entry.timestamp > entry.ttl:
                    del self._cache[cache_key]
                    self.miss_count += 1
                    return None
                
                self.hit_count += 1
                return entry.data
            
            self.miss_count += 1
            return None
    
    def set(self, prefix: str, key_data: Any, value: Any, ttl: int = 3600):
        """Set value in cache"""
        cache_key = self._generate_key(prefix, key_data)
        
        with self._lock:
            self._cache[cache_key] = CacheEntry(
                data=value,
                timestamp=time.time(),
                ttl=ttl
            )
    
    def clear_expired(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if current_time - entry.timestamp > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logging.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def clear_all(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self.hit_count = 0
            self.miss_count = 0
            logging.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "total_entries": len(self._cache),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": round(hit_rate, 3),
            "total_requests": total_requests
        }

# Global cache instance
job_cache = JobDiscoveryCache()

# Cache TTL constants (in seconds)
URL_ANALYSIS_TTL = 24 * 60 * 60  # 24 hours - URLs don't change type frequently
JOB_VALIDATION_TTL = 6 * 60 * 60  # 6 hours - Jobs might expire
LISTING_EXTRACTION_TTL = 2 * 60 * 60  # 2 hours - Listings change more frequently

def get_cached_url_analysis(url: str) -> Optional[Dict[str, Any]]:
    """Get cached URL analysis result"""
    return job_cache.get("url_analysis", url, URL_ANALYSIS_TTL)

def cache_url_analysis(url: str, result: Dict[str, Any]):
    """Cache URL analysis result"""
    job_cache.set("url_analysis", url, result, URL_ANALYSIS_TTL)

def get_cached_job_validation(url: str) -> Optional[Dict[str, Any]]:
    """Get cached job validation result"""
    return job_cache.get("job_validation", url, JOB_VALIDATION_TTL)

def cache_job_validation(url: str, result: Dict[str, Any]):
    """Cache job validation result"""
    job_cache.set("job_validation", url, result, JOB_VALIDATION_TTL)

def get_cached_listing_extraction(url: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached listing extraction result"""
    return job_cache.get("listing_extraction", url, LISTING_EXTRACTION_TTL)

def cache_listing_extraction(url: str, result: List[Dict[str, Any]]):
    """Cache listing extraction result"""
    job_cache.set("listing_extraction", url, result, LISTING_EXTRACTION_TTL)