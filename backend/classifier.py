"""
WBAE2026 – Party Classifier
Classifies news items as TMC / BJP / Others using keyword matching.
Designed to be easily replaced by an ML model later.
"""

import re
from config import PARTY_KEYWORDS


def _normalise(text: str) -> str:
    """Lowercase and strip punctuation for keyword matching."""
    return re.sub(r"[^\w\s]", " ", text.lower())


def classify_party(title: str, description: str = "", raw_text: str = "") -> str:
    """
    Returns 'TMC', 'BJP', or 'Others'.

    Strategy:
      1. Combine title + description + raw_text into one blob.
      2. Count keyword hits per party.
      3. Party with the most hits wins. Tie → 'Others'.

    Parameters
    ----------
    title       : news headline
    description : article summary / snippet
    raw_text    : full article body (optional)

    Returns
    -------
    str : 'TMC' | 'BJP' | 'Others'
    """
    corpus = _normalise(f"{title} {description} {raw_text}")

    scores: dict[str, int] = {}
    for party, keywords in PARTY_KEYWORDS.items():
        count = sum(
            len(re.findall(r"\b" + re.escape(kw) + r"\b", corpus))
            for kw in keywords
        )
        scores[party] = count

    best_party = max(scores, key=lambda p: scores[p])
    best_score = scores[best_party]

    if best_score == 0:
        return "Others"

    # Tie-breaking: multiple parties with equal score → Others
    top_parties = [p for p, s in scores.items() if s == best_score]
    return top_parties[0] if len(top_parties) == 1 else "Others"


# ── Future upgrade hook ──────────────────────────────────
def classify_party_ml(title: str, description: str = "", raw_text: str = "") -> str:
    """
    Placeholder for ML-based classification.
    Drop in a fine-tuned HuggingFace model here later:

        from transformers import pipeline
        clf = pipeline("text-classification", model="your/fine-tuned-model")
        result = clf(f"{title} {description}")
        return result[0]["label"]  # must map to TMC / BJP / Others
    """
    raise NotImplementedError("ML classifier not yet configured.")
