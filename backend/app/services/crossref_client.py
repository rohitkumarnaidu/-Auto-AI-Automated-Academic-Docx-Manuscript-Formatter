import os
import json
import logging
import requests
from urllib.parse import quote_plus
from functools import lru_cache
from typing import Dict, Any, Optional

try:
    import redis
    # Using environment variable or default
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Ping to check if alive
    redis_client.ping()
    HAS_REDIS = True
    print("✅ CrossRef Redis caching enabled.")
except Exception:
    HAS_REDIS = False
    redis_client = None
    print("ℹ️ CrossRef Redis unavailable. Utilizing fallback LRU Memory Cache.")

logger = logging.getLogger(__name__)

class CrossRefClient:
    """Client for querying the free CrossRef API to validate citations."""
    
    BASE_URL = "https://api.crossref.org/works"
    
    def __init__(self, contact_email: str = "mailto:bot@scholarform.com"):
        self.headers = {"User-Agent": f"ScholarFormValidation/1.0 ({contact_email})"}
        
    def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Attempt to fetch from Redis."""
        if HAS_REDIS:
            try:
                data = redis_client.get(f"crossref:{key}")
                if data:
                    return json.loads(data)
            except Exception:
                pass
        return None
        
    def _set_cache(self, key: str, data: Dict[str, Any], ttl: int = 86400 * 7):
        """Save results to Redis for 7 days."""
        if HAS_REDIS:
            try:
                redis_client.setex(f"crossref:{key}", ttl, json.dumps(data))
            except Exception:
                pass

    @lru_cache(maxsize=2000)
    def _fetch_api(self, query: str) -> Dict[str, Any]:
        """
        The actual network call. Wrapped in an LRU memory cache 
        so we stay within rate limits even if Redis is offline.
        """
        url = f"{self.BASE_URL}?query.bibliographic={quote_plus(query)}&rows=1"
        try:
            # Short timeout to prevent orchestrator lagging
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                items = data.get("message", {}).get("items", [])
                if items:
                    item = items[0]
                    authors = ", ".join([
                        f"{a.get('given', '')} {a.get('family', '')}".strip() 
                        for a in item.get('author', [])
                    ])
                    return {
                        "doi": item.get("DOI"),
                        "title": item.get("title", [""])[0],
                        "authors": authors,
                        "confidence": item.get("score", 0.0), # TF-IDF search relevance score
                        "url": item.get("URL")
                    }
            elif response.status_code == 429:
                logger.warning("CrossRef API rate limited. Returning empty.")
            return {}
        except requests.RequestException as e:
            logger.warning(f"CrossRef API network error: {e}. Skipping validation.")
            return {}
        except Exception as e:
            logger.warning(f"CrossRef JSON parse error: {e}")
            return {}

    def validate_citation(self, raw_text: str) -> Dict[str, Any]:
        """
        Validates a raw citation string against CrossRef.
        Returns empty dictionary if offline or not found.
        """
        if not raw_text or len(raw_text) < 10:
            return {}
            
        # Clean text
        query = raw_text.strip()
        
        # 1. Check Distributed Cache
        cached = self._get_cache(query)
        if cached:
            return cached
            
        # 2. Network Call (with Local Cache)
        result = self._fetch_api(query)
        
        # 3. Save to Distributed Cache if successful
        if result and HAS_REDIS:
            self._set_cache(query, result)
            
        return result

# Singleton export
_crossref_client = CrossRefClient()

def get_crossref_client() -> CrossRefClient:
    return _crossref_client
