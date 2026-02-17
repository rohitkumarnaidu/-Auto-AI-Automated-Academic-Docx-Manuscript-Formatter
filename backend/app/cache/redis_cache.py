import redis
import json
import logging
import hashlib
from typing import Optional, Any
from app.config.settings import settings

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Redis-based caching service for document processing results.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", host),
                port=int(os.getenv("REDIS_PORT", port)),
                db=db,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Caching will be disabled.")
            self.client = None

    def _generate_key(self, content: str, prefix: str = "grobid") -> str:
        """Generate a deterministic key based on content hash."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        return f"{prefix}:{content_hash}"

    def get_grobid_result(self, file_content: str) -> Optional[dict]:
        """Retrieve cached GROBID results for the given file content."""
        if not self.client:
            return None
            
        key = self._generate_key(file_content)
        try:
            cached_data = self.client.get(key)
            if cached_data:
                logger.info(f"Cache hit for key: {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error reading from Redis cache: {e}")
            
        return None

    def set_grobid_result(self, file_content: str, result: dict, ttl: int = 3600):
        """Cache GROBID results for the given file content with TTL."""
        if not self.client:
            return
            
        key = self._generate_key(file_content)
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(result)
            )
            logger.info(f"Cached results for key: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error writing to Redis cache: {e}")

# Global instance
import os
redis_cache = RedisCache()
