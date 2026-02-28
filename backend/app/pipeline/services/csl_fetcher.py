from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import httpx


TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
CSL_SEARCH_URL = "https://api.citationstyles.org/styles"
ZOTERO_STYLE_URL = "https://www.zotero.org/styles/{slug}"


def _local_styles() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for style_file in sorted(TEMPLATES_DIR.glob("*/styles.csl")):
        slug = style_file.parent.name.lower()
        rows.append({"slug": slug, "title": slug.upper(), "source": "local"})
    return rows


async def search_styles(query: str, limit: int = 20) -> List[Dict[str, str]]:
    query = (query or "").strip().lower()
    local = [row for row in _local_styles() if query in row["slug"] or query in row["title"].lower()]

    remote: List[Dict[str, str]] = []
    if query:
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(CSL_SEARCH_URL, params={"query": query, "limit": limit})
                resp.raise_for_status()
                payload = resp.json()
            if isinstance(payload, list):
                for item in payload:
                    if not isinstance(item, dict):
                        continue
                    slug = str(item.get("name") or item.get("slug") or "").strip().lower()
                    if not slug:
                        continue
                    remote.append(
                        {
                            "slug": slug,
                            "title": str(item.get("title") or slug),
                            "source": "remote",
                        }
                    )
        except Exception:
            # Network access can be unavailable in local/dev environments; local fallback keeps API usable.
            remote = []

    combined: Dict[str, Dict[str, str]] = {}
    for row in local + remote:
        combined[row["slug"]] = row
    return list(combined.values())[:limit]


async def fetch_style(slug: str) -> Dict[str, str]:
    style_slug = (slug or "").strip().lower()
    if not style_slug:
        raise ValueError("slug is required")

    local_path = TEMPLATES_DIR / style_slug / "styles.csl"
    if local_path.exists():
        return {
            "slug": style_slug,
            "source": "local",
            "content": local_path.read_text(encoding="utf-8"),
        }

    url = ZOTERO_STYLE_URL.format(slug=style_slug)
    async with httpx.AsyncClient(timeout=12) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    return {"slug": style_slug, "source": "remote", "content": resp.text}
