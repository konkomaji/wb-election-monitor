# WBAE2026 Phase 1 – Deployment Guide

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (Free)                          │
│   Google News RSS   │   YouTube Atom   │   Bengali RSS Feeds    │
└──────────┬──────────┴────────┬─────────┴──────────┬────────────┘
           │                   │                     │
           └───────────────────▼─────────────────────┘
                     ┌──────────────────┐
                     │  Python Backend  │  ← runs on any Linux VPS
                     │  (pipeline.py)   │    or GitHub Actions
                     │  • Fetch         │
                     │  • Classify      │
                     │  • Sentiment     │
                     │  • Deduplicate   │
                     └────────┬─────────┘
                              │ REST API (service_role key)
                     ┌────────▼─────────┐
                     │    Supabase      │  ← free tier: 500MB
                     │   PostgreSQL     │
                     │  • news_items    │
                     │  • ac_metadata   │
                     │  • fetch_logs    │
                     └────────┬─────────┘
                              │ REST API (anon key, RLS)
                     ┌────────▼─────────┐
                     │  Cloudflare      │  ← free tier
                     │  Pages (HTML)    │
                     │   Dashboard      │
                     └──────────────────┘
```

---

## Folder Structure

```
wbae2026/
├── backend/
│   ├── config.py          # All constants, AC list, keywords
│   ├── fetcher.py         # fetch_google_news / fetch_youtube / fetch_rss
│   ├── classifier.py      # classify_party()
│   ├── sentiment.py       # analyze_sentiment()
│   ├── storage.py         # store_to_supabase()
│   ├── pipeline.py        # Main runner + scheduler
│   └── requirements.txt
├── frontend/
│   └── index.html         # Single-file dashboard
└── docs/
    └── schema.sql         # Full Supabase schema
```

---

## Step 1 – Create Supabase Project

1. Go to https://supabase.com → "New Project"
2. Choose a name: `wbae2026`
3. Choose a strong DB password (save it)
4. Region: **Asia South (Mumbai)**
5. Wait ~2 minutes for provisioning

---

## Step 2 – Set Up Database Schema

1. In Supabase dashboard → **SQL Editor** → "New Query"
2. Paste the entire contents of `docs/schema.sql`
3. Click **Run** (green button)
4. Verify in **Table Editor** that `news_items`, `ac_metadata`, `fetch_logs` appear

---

## Step 3 – Get API Keys

1. Go to **Settings → API**
2. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon / public key** → `SUPABASE_ANON_KEY` (for frontend)
   - **service_role / secret key** → `SUPABASE_SERVICE_KEY` (for backend only — never expose)

---

## Step 4 – Configure Backend

Create `backend/.env`:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=eyJhbG...your_service_role_key
SUPABASE_ANON_KEY=eyJhbG...your_anon_key
```

Install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Test run (single cycle):
```bash
python pipeline.py
```

---

## Step 5 – Run Backend as a Service

**Option A – systemd (Ubuntu VPS)**
```ini
# /etc/systemd/system/wbae2026.service
[Unit]
Description=WBAE2026 Monitor
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/wbae2026/backend
ExecStart=/home/ubuntu/wbae2026/backend/venv/bin/python pipeline.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable wbae2026
sudo systemctl start wbae2026
sudo journalctl -u wbae2026 -f   # watch logs
```

**Option B – GitHub Actions (free, cron)**
```yaml
# .github/workflows/fetch.yml
name: Fetch Data
on:
  schedule:
    - cron: '*/10 * * * *'   # every 10 minutes
  workflow_dispatch:

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: python backend/pipeline.py --single-cycle
        env:
          SUPABASE_URL:         ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        timeout-minutes: 8
```
Add secrets in GitHub → Settings → Secrets → Actions.

---

## Step 6 – Deploy Frontend to Cloudflare Pages

1. Edit `frontend/index.html`:
   - Replace `YOUR_SUPABASE_URL` with your Supabase URL
   - Replace `YOUR_SUPABASE_ANON_KEY` with your anon key
   - (The anon key is safe to expose — RLS policies protect the data)

2. Push `frontend/` to a GitHub repo

3. In Cloudflare:
   - Dashboard → **Pages** → "Create a project"
   - Connect GitHub → select your repo
   - Build settings:
     - Framework: **None**
     - Build command: *(leave empty)*
     - Output directory: `frontend`
   - Click **Save and Deploy**

4. Your dashboard will be live at `https://wbae2026.pages.dev` (or custom domain)

---

## Step 7 – Verify End-to-End

1. Check Supabase Table Editor → `news_items` should start filling up
2. Open your Cloudflare Pages URL
3. Select any AC from the sidebar
4. Confirm live data loads in the feed

---

## Free Tier Limits & Management

| Service       | Free Limit        | Action if exceeded          |
|---------------|-------------------|-----------------------------|
| Supabase DB   | 500 MB storage    | Add cleanup cron (see below)|
| Supabase API  | 50,000 req/month  | Cache reads on frontend     |
| Cloudflare    | Unlimited static  | No limit concerns           |
| GitHub Actions| 2,000 min/month   | Reduce fetch frequency      |

**Data retention cleanup** (add to Supabase → Database → Functions):
```sql
-- Run daily to keep only 30 days of data
DELETE FROM news_items
WHERE timestamp < NOW() - INTERVAL '30 days';
```

---

## Future Upgrade Path

1. **ML Classification**: Swap `classify_party()` in `classifier.py` with a
   fine-tuned `distilbert` or `indicbert` model trained on WB political text

2. **Bengali NLP Sentiment**: Integrate `indic-nlp-library` or
   `bangla-bert-base` from HuggingFace for Bengali sentiment

3. **YouTube Data API v3**: Replace the Atom workaround with proper
   YouTube API (10,000 free units/day) for better search results

4. **Alerting**: Add a Telegram bot notification when a constituency
   sentiment drops sharply negative (using python-telegram-bot)

5. **Historical Analysis**: Add a time-series chart (Chart.js) showing
   sentiment over weeks using the `hourly_trends` view

6. **Map View**: Integrate Leaflet.js with WB constituency GeoJSON for
   a choropleth sentiment map

7. **Scalability**: Move to Supabase Realtime subscriptions so the frontend
   updates automatically without polling
