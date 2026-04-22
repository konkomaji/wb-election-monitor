"""
WBAE2026 Phase 1 – Main Pipeline & Scheduler
Runs every 10 minutes, cycling through all 150 ACs.
"""

import logging
import random
import time
from datetime import datetime, timezone

import schedule

from classifier import classify_party
from config import ALL_AC, FETCH_INTERVAL_MINUTES
from fetcher import fetch_all_for_ac
from sentiment import analyze_sentiment
from storage import log_fetch_run, store_to_supabase

# ──────────────────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("wbae2026.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("pipeline")


# ──────────────────────────────────────────────────────────
# Enrichment: tag party + sentiment onto raw items
# ──────────────────────────────────────────────────────────

def enrich(items: list[dict]) -> list[dict]:
    enriched = []
    for item in items:
        title = item.get("title", "")
        desc  = item.get("description", "")
        raw   = item.get("raw_text", "")

        item["party_tag"]       = classify_party(title, desc, raw)
        label, score            = analyze_sentiment(title, desc, raw)
        item["sentiment"]       = label
        item["sentiment_score"] = score

        enriched.append(item)
    return enriched


# ──────────────────────────────────────────────────────────
# Single-AC pipeline
# ──────────────────────────────────────────────────────────

def run_ac_pipeline(ac_name: str) -> None:
    start = time.perf_counter()
    logger.info("▶ Processing AC: %s", ac_name)

    raw_items = fetch_all_for_ac(ac_name)
    enriched  = enrich(raw_items)
    stored, _ = store_to_supabase(enriched)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    log_fetch_run(
        source="all",
        ac_name=ac_name,
        items_fetched=len(raw_items),
        items_stored=stored,
        duration_ms=elapsed_ms,
    )
    logger.info("✔ %s done | fetched=%d stored=%d (%dms)",
                ac_name, len(raw_items), stored, elapsed_ms)


# ──────────────────────────────────────────────────────────
# Full cycle: runs all 150 ACs in random order to avoid
# rate-limit patterns on repeated runs
# ──────────────────────────────────────────────────────────

def run_full_cycle() -> None:
    cycle_start = datetime.now(timezone.utc).isoformat()
    logger.info("═══ Cycle start %s (%d ACs) ═══", cycle_start, len(ALL_AC))

    ac_list = list(ALL_AC)
    random.shuffle(ac_list)

    for idx, ac in enumerate(ac_list, 1):
        logger.info("[%d/%d]", idx, len(ac_list))
        try:
            run_ac_pipeline(ac)
        except Exception as exc:
            logger.error("Error in AC %s: %s", ac, exc, exc_info=True)

        # Polite inter-AC delay: 1–2 seconds
        time.sleep(random.uniform(1.0, 2.0))

    logger.info("═══ Cycle complete ═══")


# ──────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logger.info("WBAE2026 Phase 1 Monitor starting …")

    # Run immediately on startup
    run_full_cycle()

    if "--single-cycle" in sys.argv:
        logger.info("Single cycle complete. Exiting.")
        sys.exit(0)

    # Schedule every N minutes
    schedule.every(FETCH_INTERVAL_MINUTES).minutes.do(run_full_cycle)

    logger.info(
        "Scheduler active – running every %d minutes. Press Ctrl+C to stop.",
        FETCH_INTERVAL_MINUTES,
    )
    while True:
        schedule.run_pending()
        time.sleep(30)
