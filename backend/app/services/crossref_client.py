import json
import logging
import os
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

import requests

from app.config.settings import settings

logger = logging.getLogger(__name__)

try:
    import redis

    redis_enabled = os.getenv("REDIS_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
    if not redis_enabled:
        raise RuntimeError("REDIS_ENABLED=false")

    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    HAS_REDIS = True
    logger.info("CrossRef Redis caching enabled.")
except Exception:
    HAS_REDIS = False
    redis_client = None
    logger.info("CrossRef Redis unavailable. Using fallback in-memory cache.")


class CrossRefClient:
    """Client for querying the free CrossRef API to validate citations."""

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, contact_email: Optional[str] = None):
        email = contact_email or getattr(settings, "CROSSREF_MAILTO", "mailto:bot@scholarform.com")
        self.headers = {"User-Agent": f"ScholarFormValidation/1.0 ({email})"}
        # Instance-level cache (no global lru_cache memory leak).
        self._api_cache: Dict[str, Dict[str, Any]] = {}

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

    def _fetch_api(self, query: str) -> Dict[str, Any]:
        """
        The actual network call with instance-level dict cache.
        Avoids @lru_cache on instance method which can leak memory.
        """
        # Check instance cache first.
        if query in self._api_cache:
            return self._api_cache[query]

        url = f"{self.BASE_URL}?query.bibliographic={quote_plus(query)}&rows=1"
        try:
            # Short timeout to prevent orchestrator lagging.
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                items = data.get("message", {}).get("items", [])
                if items:
                    item = items[0]
                    authors = ", ".join(
                        [
                            f"{a.get('given', '')} {a.get('family', '')}".strip()
                            for a in item.get("author", [])
                        ]
                    )
                    result = {
                        "doi": item.get("DOI"),
                        "title": item.get("title", [""])[0],
                        "authors": authors,
                        # TF-IDF search relevance score from CrossRef.
                        "confidence": item.get("score", 0.0),
                        "url": item.get("URL"),
                    }
                    self._api_cache[query] = result
                    return result
            elif response.status_code == 429:
                logger.warning("CrossRef API rate limited. Returning empty.")
            return {}
        except requests.RequestException as e:
            logger.warning("CrossRef API network error: %s. Skipping validation.", e)
            return {}
        except Exception as e:
            logger.warning("CrossRef JSON parse error: %s", e)
            return {}
        finally:
            # Trim cache to prevent unbounded growth (keep last 2000).
            if len(self._api_cache) > 2000:
                keys = list(self._api_cache.keys())
                for k in keys[: len(keys) - 2000]:
                    del self._api_cache[k]

    def validate_citation(self, raw_text: str) -> Dict[str, Any]:
        """
        Validates a raw citation string against CrossRef.
        Returns empty dictionary if offline or not found.
        """
        if not raw_text or len(raw_text) < 10:
            return {}

        query = raw_text.strip()

        # 1. Check distributed cache.
        cached = self._get_cache(query)
        if cached:
            return cached

        # 2. Network call (with local cache).
        result = self._fetch_api(query)

        # 3. Save to distributed cache if successful.
        if result and HAS_REDIS:
            self._set_cache(query, result)

        return result


_crossref_client = CrossRefClient()


def get_crossref_client() -> CrossRefClient:
    return _crossref_client
