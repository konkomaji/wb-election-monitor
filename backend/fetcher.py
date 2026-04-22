"""
WBAE2026 – Data Fetcher
Provides three fetch functions:
  fetch_google_news(ac_name)  → list[dict]
  fetch_youtube(ac_name)      → list[dict]
  fetch_rss(feed)             → list[dict]

Each returns a normalised list of news item dicts.
"""

import hashlib
import logging
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests
import feedparser

from config import (
    GOOGLE_NEWS_RSS_TEMPLATE,
    MAX_ITEMS_PER_AC,
    REQUEST_TIMEOUT,
    RSS_FEEDS,
    USER_AGENT,
)

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": USER_AGENT}


# ──────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────

def _make_hash(text: str) -> str:
    """SHA-256 hash of text for deduplication."""
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_get(url: str) -> requests.Response | None:
    """GET with timeout and graceful error handling."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        logger.warning("HTTP error fetching %s: %s", url, exc)
        return None


# ──────────────────────────────────────────────────────────
# 1. Google News RSS
# ──────────────────────────────────────────────────────────

def fetch_google_news(ac_name: str) -> list[dict]:
    """
    Fetch latest Google News results for an AC via RSS.

    Query format: '<AC name> West Bengal election 2026'
    """
    query = quote_plus(f"{ac_name} West Bengal election 2026 politics")
    url = GOOGLE_NEWS_RSS_TEMPLATE.format(query=query)

    resp = _safe_get(url)
    if resp is None:
        return []

    items: list[dict] = []
    try:
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if channel is None:
            return []

        for entry in channel.findall("item")[:MAX_ITEMS_PER_AC]:
            title = (entry.findtext("title") or "").strip()
            link  = (entry.findtext("link")  or "").strip()
            desc  = (entry.findtext("description") or "").strip()
            pub   = entry.findtext("pubDate") or _now_iso()

            if not title or not link:
                continue

            items.append({
                "ac_name":      ac_name,
                "source":       "google_news",
                "title":        title,
                "description":  desc,
                "url":          link,
                "raw_text":     f"{title} {desc}",
                "timestamp":    pub,
                "content_hash": _make_hash(title),
            })
    except ET.ParseError as exc:
        logger.error("XML parse error for Google News (%s): %s", ac_name, exc)

    logger.info("Google News → %s: %d items", ac_name, len(items))
    return items


# ──────────────────────────────────────────────────────────
# 2. YouTube
# ──────────────────────────────────────────────────────────

YOUTUBE_SEARCH_RSS = "https://www.youtube.com/feeds/videos.xml?search_query={query}"
YOUTUBE_API_URL    = "https://www.googleapis.com/youtube/v3/search"

def fetch_youtube(ac_name: str) -> list[dict]:
    """
    Fetch latest YouTube videos mentioning the AC.
    Priority: YouTube Data API v3 (if YOUTUBE_API_KEY set)
    Fallback: Public RSS (unreliable for search)
    """
    from config import YOUTUBE_API_KEY
    query = f"{ac_name} West Bengal election 2026 politics"
    
    # Strategy A: YouTube Data API v3 (Official & Reliable)
    if YOUTUBE_API_KEY:
        params = {
            "part":       "snippet",
            "q":          query,
            "maxResults": MAX_ITEMS_PER_AC,
            "order":      "date",
            "type":       "video",
            "key":        YOUTUBE_API_KEY,
        }
        resp = _safe_get(f"{YOUTUBE_API_URL}?{quote_plus('')}") # Use requests params
        try:
            r = requests.get(YOUTUBE_API_URL, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            items = []
            for item in data.get("items", []):
                snippet = item["snippet"]
                v_id = item["id"]["videoId"]
                items.append({
                    "ac_name":      ac_name,
                    "source":       "youtube",
                    "title":        snippet["title"],
                    "description":  snippet["description"],
                    "url":          f"https://www.youtube.com/watch?v={v_id}",
                    "raw_text":     f"{snippet['title']} {snippet['description']}",
                    "timestamp":    snippet["publishedAt"],
                    "content_hash": _make_hash(snippet["title"]),
                })
            logger.info("YouTube API → %s: %d items", ac_name, len(items))
            return items
        except Exception as exc:
            logger.warning("YouTube API failed, trying RSS fallback: %s", exc)

    # Strategy B: RSS Fallback (Unreliable for search queries)
    url = YOUTUBE_SEARCH_RSS.format(query=quote_plus(query))
    resp = _safe_get(url)
    if resp is None:
        return []

    items: list[dict] = []
    try:
        feed = feedparser.parse(resp.content)
        # If YouTube returns 400 or empty, feedparser will have an empty list
        for entry in getattr(feed, "entries", [])[:MAX_ITEMS_PER_AC]:
            title     = getattr(entry, "title", "").strip()
            link      = getattr(entry, "link", "").strip()
            summary   = getattr(entry, "summary", "").strip()
            published = getattr(entry, "published", _now_iso())

            if not title or not link:
                continue

            items.append({
                "ac_name":      ac_name,
                "source":       "youtube",
                "title":        title,
                "description":  summary,
                "url":          link,
                "raw_text":     f"{title} {summary}",
                "timestamp":    published,
                "content_hash": _make_hash(title),
            })
    except Exception:
        pass # Silence noisy YouTube RSS errors

    logger.info("YouTube RSS → %s: %d items", ac_name, len(items))
    return items


# ──────────────────────────────────────────────────────────
# 3. Bengali / National RSS Feeds
# ──────────────────────────────────────────────────────────

def fetch_rss(feed: dict, ac_name: str = "") -> list[dict]:
    """
    Fetch a generic RSS/Atom feed and filter entries containing
    the AC name (if provided).

    Parameters
    ----------
    feed    : one entry from config.RSS_FEEDS
    ac_name : if set, only return entries mentioning this AC
    """
    resp = _safe_get(feed["url"])
    if resp is None:
        return []

    items: list[dict] = []
    try:
        parsed = feedparser.parse(resp.content)
        for entry in parsed.entries:
            title   = getattr(entry, "title",   "").strip()
            link    = getattr(entry, "link",    "").strip()
            summary = getattr(entry, "summary", "").strip()
            pub     = getattr(entry, "published", _now_iso())

            if not title:
                continue

            combined = f"{title} {summary}".lower()

            # Filter by AC if specified
            if ac_name and ac_name.lower() not in combined:
                continue

            items.append({
                "ac_name":      ac_name or "General",
                "source":       "rss",
                "title":        title,
                "description":  summary,
                "url":          link,
                "raw_text":     f"{title} {summary}",
                "timestamp":    pub,
                "content_hash": _make_hash(title),
            })

            if len(items) >= MAX_ITEMS_PER_AC:
                break

    except Exception as exc:
        logger.error("RSS parse error [%s]: %s", feed["name"], exc)

    logger.info("RSS [%s] → %s: %d items", feed["name"], ac_name or "*", len(items))
    return items


# ──────────────────────────────────────────────────────────
# 4. Fetch all sources for one AC
# ──────────────────────────────────────────────────────────

def fetch_all_for_ac(ac_name: str) -> list[dict]:
    """Aggregate all sources for a single constituency."""
    results: list[dict] = []

    results.extend(fetch_google_news(ac_name))
    time.sleep(0.3)   # polite delay

    results.extend(fetch_youtube(ac_name))
    time.sleep(0.3)

    for feed in RSS_FEEDS:
        results.extend(fetch_rss(feed, ac_name))
        time.sleep(0.2)

    return results
