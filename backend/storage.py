"""
WBAE2026 – Supabase Storage Layer
Handles deduplication and batch inserts.
"""

import logging
from datetime import datetime, timezone

import requests

from config import SUPABASE_SERVICE_KEY, SUPABASE_URL

logger = logging.getLogger(__name__)

# Supabase REST API endpoint
REST_BASE = f"{SUPABASE_URL}/rest/v1"

HEADERS = {
    "apikey":        SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}


def _upsert_row(row: dict) -> bool:
    """
    Upsert a single row into news_items.
    Uses content_hash as the conflict key to deduplicate.
    Returns True if inserted/updated, False on error.
    """
    url = f"{REST_BASE}/news_items"
    params = {"on_conflict": "content_hash"}

    try:
        resp = requests.post(
            url, json=row, headers=HEADERS, params=params, timeout=10
        )
        if resp.status_code in (200, 201):
            return True
        if resp.status_code == 409:
            logger.debug("Duplicate skipped: %s", row.get("content_hash", ""))
            return False
        logger.warning(
            "Supabase upsert returned %s: %s", resp.status_code, resp.text[:200]
        )
        return False
    except requests.RequestException as exc:
        logger.error("Supabase connection error: %s", exc)
        return False


def store_to_supabase(items: list[dict]) -> tuple[int, int]:
    """
    Store a list of enriched news items.

    Parameters
    ----------
    items : list of dicts with keys:
            ac_name, source, title, description, url,
            party_tag, sentiment, sentiment_score,
            raw_text, content_hash, timestamp

    Returns
    -------
    (stored_count, duplicate_count)
    """
    stored = 0
    dupes = 0

    for item in items:
        # Ensure timestamp is ISO format string
        ts = item.get("timestamp", "")
        if not ts:
            ts = datetime.now(timezone.utc).isoformat()
        item["timestamp"] = ts

        success = _upsert_row(item)
        if success:
            stored += 1
        else:
            dupes += 1

    logger.info("Stored %d | Duplicates skipped %d", stored, dupes)
    return stored, dupes


def log_fetch_run(
    source: str,
    ac_name: str,
    items_fetched: int,
    items_stored: int,
    duration_ms: int,
    error: str = "",
) -> None:
    """Write a fetch log entry to fetch_logs table."""
    url = f"{REST_BASE}/fetch_logs"
    payload = {
        "source":        source,
        "ac_name":       ac_name,
        "items_fetched": items_fetched,
        "items_stored":  items_stored,
        "duration_ms":   duration_ms,
        "error_message": error,
    }
    try:
        requests.post(url, json=payload, headers=HEADERS, timeout=5)
    except requests.RequestException as exc:
        logger.warning("Could not write fetch log: %s", exc)
