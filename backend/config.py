"""
WBAE2026 Phase 1 Digital Monitoring System
Configuration & Constants
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────────────────
# Supabase credentials (set in .env file)
# ──────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")   # backend writes
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")         # frontend reads
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")             # optional for v3 API

# ──────────────────────────────────────────────────────────
# Scheduler
# ──────────────────────────────────────────────────────────
FETCH_INTERVAL_MINUTES = 10

# ──────────────────────────────────────────────────────────
# All 150 West Bengal Assembly Constituencies
# ──────────────────────────────────────────────────────────
ALL_AC = [
    "Mekliganj", "Mathabhanga", "Cooch Behar Uttar", "Cooch Behar Dakshin",
    "Sitalkuchi", "Sitai", "Dinhata", "Natabari", "Tufanganj", "Kumargram",
    "Kalchini", "Alipurduars", "Falakata", "Madarihat", "Dhupguri", "Maynaguri",
    "Jalpaiguri", "Rajganj", "Dabgram-Phulbari", "Mal", "Nagrakata", "Kalimpong",
    "Darjeeling", "Kurseong", "Matigara-Naxalbari", "Siliguri", "Phansidewa",
    "Chopra", "Islampur", "Goalpokhar", "Chakulia", "Karandighi", "Hemtabad",
    "Kaliaganj", "Raiganj", "Itahar", "Kushmandi", "Kumarganj", "Balurghat",
    "Tapan", "Gangarampur", "Harirampur", "Habibpur", "Gazole", "Chanchal",
    "Harishchandrapur", "Malatipur", "Ratua", "Manikchak", "Maldaha",
    "English Bazar", "Mothabari", "Sujapur", "Baisnabnagar", "Farakka",
    "Samserganj", "Suti", "Jangipur", "Raghunathganj", "Sagardighi", "Lalgola",
    "Bhagabangola", "Raninagar", "Murshidabad", "Nabagram", "Khargram",
    "Burwan", "Kandi", "Bharatpur", "Rejinagar", "Beldanga", "Baharampur",
    "Hariharpara", "Naoda", "Domkal", "Jalangi", "Tamluk", "Panskura Purba",
    "Panskura Paschim", "Moyna", "Nandakumar", "Mahisadal", "Haldia",
    "Nandigram", "Chandipur", "Patashpur", "Kanthi Uttar", "Bhagabanpur",
    "Khejuri", "Kanthi Dakshin", "Ramnagar", "Egra", "Dantan", "Nayagram",
    "Gopiballavpur", "Jhargram", "Keshiary", "Kharagpur Sadar", "Narayangarh",
    "Sabang", "Pingla", "Kharagpur", "Debra", "Daspur", "Ghatal",
    "Chandrakona", "Garbeta", "Salboni", "Keshpur", "Medinipur", "Binpur",
    "Bandwan", "Balarampur", "Baghmundi", "Joypur", "Purulia", "Manbazar",
    "Kashipur", "Para", "Raghunathpur", "Saltora", "Chhatna", "Ranibandh",
    "Raipur", "Taldangra", "Bankura", "Barjora", "Onda", "Bishnupur",
    "Katulpur", "Indas", "Sonamukhi", "Pandabeswar", "Durgapur Purba",
    "Durgapur Paschim", "Raniganj", "Jamuria", "Asansol Dakshin", "Asansol Uttar",
    "Kulti", "Barabani", "Dubrajpur", "Suri", "Bolpur", "Nanoor", "Labpur",
    "Sainthia", "Mayureswar", "Rampurhat", "Hansan", "Nalhati", "Murarai",
]

# ──────────────────────────────────────────────────────────
# Party Classification Keywords
# ──────────────────────────────────────────────────────────
PARTY_KEYWORDS = {
    "TMC": [
        "tmc", "trinamool", "mamata", "mamata banerjee", "aitc",
        "all india trinamool", "didi", "abhishek banerjee",
    ],
    "BJP": [
        "bjp", "modi", "narendra modi", "suvendu adhikari",
        "bharatiya janata", "amit shah", "dilip ghosh",
    ],
}

# ──────────────────────────────────────────────────────────
# Sentiment Lexicons (rule-based, Bengali + English)
# ──────────────────────────────────────────────────────────
POSITIVE_KEYWORDS = [
    "victory", "win", "winning", "develop", "development", "progress",
    "success", "achieve", "growth", "welfare", "benefit", "support",
    "rally", "majority", "lead", "ahead", "positive", "good",
    "জয়", "উন্নয়ন", "সাফল্য", "জিতল", "এগিয়ে",
]

NEGATIVE_KEYWORDS = [
    "defeat", "loss", "lose", "violence", "clash", "attack", "bomb",
    "murder", "crime", "corruption", "scam", "protest", "riot",
    "arrest", "accused", "controversy", "fail", "failure", "problem",
    "হিংসা", "সংঘর্ষ", "দুর্নীতি", "গ্রেফতার", "বিতর্ক", "পরাজয়",
]

# ──────────────────────────────────────────────────────────
# RSS Feed Sources (Bengali + National covering WB politics)
# ──────────────────────────────────────────────────────────
RSS_FEEDS = [
    {
        "name": "Sangbad Pratidin",
        "url": "https://www.sangbadpratidin.in/feed/",
        "language": "bn",
    },
    {
        "name": "Times of India WB",
        "url": "https://timesofindia.indiatimes.com/rssfeeds/2128936835.cms",
        "language": "en",
    },
    {
        "name": "NDTV India",
        "url": "https://feeds.feedburner.com/ndtvindia",
        "language": "en",
    },
    {
        "name": "India Today WB",
        "url": "https://www.indiatoday.in/rss/home",
        "language": "en",
    },
]

# ──────────────────────────────────────────────────────────
# Google News RSS template
# ──────────────────────────────────────────────────────────
GOOGLE_NEWS_RSS_TEMPLATE = (
    "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)

# ──────────────────────────────────────────────────────────
# Request settings
# ──────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 15       # seconds
MAX_ITEMS_PER_AC = 10      # max news items per AC per fetch cycle
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
