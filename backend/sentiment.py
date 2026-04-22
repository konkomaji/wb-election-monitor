"""
WBAE2026 – Sentiment Analyser
Rule-based scoring with a clean interface for future ML upgrade.
"""

import re
from config import POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS


def _normalise(text: str) -> str:
    return re.sub(r"[^\w\s]", " ", text.lower())


def _count_hits(corpus: str, keywords: list[str]) -> int:
    return sum(
        len(re.findall(r"\b" + re.escape(kw) + r"\b", corpus))
        for kw in keywords
    )


def analyze_sentiment(
    title: str, description: str = "", raw_text: str = ""
) -> tuple[str, float]:
    """
    Returns (label, score) where:
      label : 'Positive' | 'Negative' | 'Neutral'
      score : float in [-1.0, +1.0]

    Algorithm
    ---------
    score = (pos_hits - neg_hits) / (pos_hits + neg_hits + 1)
    Thresholds:
      score > +0.05  → Positive
      score < -0.05  → Negative
      otherwise      → Neutral
    """
    corpus = _normalise(f"{title} {description} {raw_text}")

    pos = _count_hits(corpus, POSITIVE_KEYWORDS)
    neg = _count_hits(corpus, NEGATIVE_KEYWORDS)
    total = pos + neg

    if total == 0:
        return "Neutral", 0.0

    score = round((pos - neg) / (total + 1), 4)

    if score > 0.05:
        label = "Positive"
    elif score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return label, score


# ── Future upgrade hook ──────────────────────────────────
def analyze_sentiment_ml(
    title: str, description: str = "", raw_text: str = ""
) -> tuple[str, float]:
    """
    Placeholder for ML sentiment model.
    Example using HuggingFace:

        from transformers import pipeline
        sa = pipeline("sentiment-analysis",
                      model="cardiffnlp/twitter-roberta-base-sentiment")
        result = sa(f"{title} {description}", truncation=True)[0]
        label_map = {"LABEL_0": "Negative", "LABEL_1": "Neutral",
                     "LABEL_2": "Positive"}
        label = label_map[result["label"]]
        score = result["score"] if label == "Positive" else -result["score"]
        return label, round(score, 4)
    """
    raise NotImplementedError("ML sentiment model not yet configured.")
