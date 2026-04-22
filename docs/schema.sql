-- ============================================================
-- WBAE2026 PHASE 1 Digital Monitoring System
-- Supabase Schema
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ──────────────────────────────────────────────────────────
-- TABLE: news_items
-- Core table for all ingested media signals
-- ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS news_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ac_name         TEXT NOT NULL,
    source          TEXT NOT NULL CHECK (source IN ('google_news', 'youtube', 'rss')),
    title           TEXT NOT NULL,
    description     TEXT,
    url             TEXT NOT NULL,
    party_tag       TEXT NOT NULL DEFAULT 'Others' CHECK (party_tag IN ('TMC', 'BJP', 'Others')),
    sentiment       TEXT NOT NULL DEFAULT 'Neutral' CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
    sentiment_score FLOAT DEFAULT 0.0,          -- -1.0 (very negative) to +1.0 (very positive)
    raw_text        TEXT,
    content_hash    TEXT UNIQUE,                -- SHA256 of title for deduplication
    is_processed    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────
-- TABLE: ac_metadata
-- Reference table for all WB Assembly Constituencies
-- ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ac_metadata (
    id          SERIAL PRIMARY KEY,
    ac_name     TEXT UNIQUE NOT NULL,
    district    TEXT,
    division    TEXT,
    is_active   BOOLEAN DEFAULT TRUE
);

-- ──────────────────────────────────────────────────────────
-- TABLE: fetch_logs
-- Tracks scheduler runs for monitoring and debugging
-- ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fetch_logs (
    id              SERIAL PRIMARY KEY,
    run_at          TIMESTAMPTZ DEFAULT NOW(),
    source          TEXT,
    ac_name         TEXT,
    items_fetched   INTEGER DEFAULT 0,
    items_stored    INTEGER DEFAULT 0,
    error_message   TEXT,
    duration_ms     INTEGER
);

-- ──────────────────────────────────────────────────────────
-- INDEXES for query performance
-- ──────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_news_ac_name      ON news_items (ac_name);
CREATE INDEX IF NOT EXISTS idx_news_timestamp    ON news_items (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_news_party_tag    ON news_items (party_tag);
CREATE INDEX IF NOT EXISTS idx_news_sentiment    ON news_items (sentiment);
CREATE INDEX IF NOT EXISTS idx_news_source       ON news_items (source);
CREATE INDEX IF NOT EXISTS idx_news_ac_time      ON news_items (ac_name, timestamp DESC);

-- ──────────────────────────────────────────────────────────
-- ROW-LEVEL SECURITY (enable for Supabase public API)
-- ──────────────────────────────────────────────────────────
ALTER TABLE news_items   ENABLE ROW LEVEL SECURITY;
ALTER TABLE ac_metadata  ENABLE ROW LEVEL SECURITY;
ALTER TABLE fetch_logs   ENABLE ROW LEVEL SECURITY;

-- Public read access (dashboard uses anon key)
CREATE POLICY "Allow public read on news_items"
    ON news_items FOR SELECT USING (true);

CREATE POLICY "Allow public read on ac_metadata"
    ON ac_metadata FOR SELECT USING (true);

-- Backend writes via service role key only (no policy needed for service_role)

-- ──────────────────────────────────────────────────────────
-- SEED: Insert all 150 West Bengal Assembly Constituencies
-- ──────────────────────────────────────────────────────────
INSERT INTO ac_metadata (ac_name, district, division) VALUES
('Mekliganj',          'Cooch Behar', 'Jalpaiguri'),
('Mathabhanga',        'Cooch Behar', 'Jalpaiguri'),
('Cooch Behar Uttar',  'Cooch Behar', 'Jalpaiguri'),
('Cooch Behar Dakshin','Cooch Behar', 'Jalpaiguri'),
('Sitalkuchi',         'Cooch Behar', 'Jalpaiguri'),
('Sitai',              'Cooch Behar', 'Jalpaiguri'),
('Dinhata',            'Cooch Behar', 'Jalpaiguri'),
('Natabari',           'Cooch Behar', 'Jalpaiguri'),
('Tufanganj',          'Cooch Behar', 'Jalpaiguri'),
('Kumargram',          'Alipurduar',  'Jalpaiguri'),
('Kalchini',           'Alipurduar',  'Jalpaiguri'),
('Alipurduars',        'Alipurduar',  'Jalpaiguri'),
('Falakata',           'Alipurduar',  'Jalpaiguri'),
('Madarihat',          'Alipurduar',  'Jalpaiguri'),
('Dhupguri',           'Jalpaiguri',  'Jalpaiguri'),
('Maynaguri',          'Jalpaiguri',  'Jalpaiguri'),
('Jalpaiguri',         'Jalpaiguri',  'Jalpaiguri'),
('Rajganj',            'Jalpaiguri',  'Jalpaiguri'),
('Dabgram-Phulbari',   'Jalpaiguri',  'Jalpaiguri'),
('Mal',                'Jalpaiguri',  'Jalpaiguri'),
('Nagrakata',          'Jalpaiguri',  'Jalpaiguri'),
('Kalimpong',          'Kalimpong',   'Jalpaiguri'),
('Darjeeling',         'Darjeeling',  'Jalpaiguri'),
('Kurseong',           'Darjeeling',  'Jalpaiguri'),
('Matigara-Naxalbari', 'Darjeeling',  'Jalpaiguri'),
('Siliguri',           'Darjeeling',  'Jalpaiguri'),
('Phansidewa',         'Darjeeling',  'Jalpaiguri'),
('Chopra',             'Uttar Dinajpur','Uttar Dinajpur'),
('Islampur',           'Uttar Dinajpur','Uttar Dinajpur'),
('Goalpokhar',         'Uttar Dinajpur','Uttar Dinajpur'),
('Chakulia',           'Uttar Dinajpur','Uttar Dinajpur'),
('Karandighi',         'Uttar Dinajpur','Uttar Dinajpur'),
('Hemtabad',           'Uttar Dinajpur','Uttar Dinajpur'),
('Kaliaganj',          'Uttar Dinajpur','Uttar Dinajpur'),
('Raiganj',            'Uttar Dinajpur','Uttar Dinajpur'),
('Itahar',             'Uttar Dinajpur','Uttar Dinajpur'),
('Kushmandi',          'Dakshin Dinajpur','Uttar Dinajpur'),
('Kumarganj',          'Dakshin Dinajpur','Uttar Dinajpur'),
('Balurghat',          'Dakshin Dinajpur','Uttar Dinajpur'),
('Tapan',              'Dakshin Dinajpur','Uttar Dinajpur'),
('Gangarampur',        'Dakshin Dinajpur','Uttar Dinajpur'),
('Harirampur',         'Dakshin Dinajpur','Uttar Dinajpur'),
('Habibpur',           'Malda',        'Malda'),
('Gazole',             'Malda',        'Malda'),
('Chanchal',           'Malda',        'Malda'),
('Harishchandrapur',   'Malda',        'Malda'),
('Malatipur',          'Malda',        'Malda'),
('Ratua',              'Malda',        'Malda'),
('Manikchak',          'Malda',        'Malda'),
('Maldaha',            'Malda',        'Malda'),
('English Bazar',      'Malda',        'Malda'),
('Mothabari',          'Malda',        'Malda'),
('Sujapur',            'Malda',        'Malda'),
('Baisnabnagar',       'Malda',        'Malda'),
('Farakka',            'Murshidabad',  'Murshidabad'),
('Samserganj',         'Murshidabad',  'Murshidabad'),
('Suti',               'Murshidabad',  'Murshidabad'),
('Jangipur',           'Murshidabad',  'Murshidabad'),
('Raghunathganj',      'Murshidabad',  'Murshidabad'),
('Sagardighi',         'Murshidabad',  'Murshidabad'),
('Lalgola',            'Murshidabad',  'Murshidabad'),
('Bhagabangola',       'Murshidabad',  'Murshidabad'),
('Raninagar',          'Murshidabad',  'Murshidabad'),
('Murshidabad',        'Murshidabad',  'Murshidabad'),
('Nabagram',           'Murshidabad',  'Murshidabad'),
('Khargram',           'Murshidabad',  'Murshidabad'),
('Burwan',             'Murshidabad',  'Murshidabad'),
('Kandi',              'Murshidabad',  'Murshidabad'),
('Bharatpur',          'Murshidabad',  'Murshidabad'),
('Rejinagar',          'Murshidabad',  'Murshidabad'),
('Beldanga',           'Murshidabad',  'Murshidabad'),
('Baharampur',         'Murshidabad',  'Murshidabad'),
('Hariharpara',        'Murshidabad',  'Murshidabad'),
('Naoda',              'Murshidabad',  'Murshidabad'),
('Domkal',             'Murshidabad',  'Murshidabad'),
('Jalangi',            'Murshidabad',  'Murshidabad'),
('Tamluk',             'Purba Medinipur','Medinipur'),
('Panskura Purba',     'Purba Medinipur','Medinipur'),
('Panskura Paschim',   'Purba Medinipur','Medinipur'),
('Moyna',              'Purba Medinipur','Medinipur'),
('Nandakumar',         'Purba Medinipur','Medinipur'),
('Mahisadal',          'Purba Medinipur','Medinipur'),
('Haldia',             'Purba Medinipur','Medinipur'),
('Nandigram',          'Purba Medinipur','Medinipur'),
('Chandipur',          'Purba Medinipur','Medinipur'),
('Patashpur',          'Purba Medinipur','Medinipur'),
('Kanthi Uttar',       'Purba Medinipur','Medinipur'),
('Bhagabanpur',        'Purba Medinipur','Medinipur'),
('Khejuri',            'Purba Medinipur','Medinipur'),
('Kanthi Dakshin',     'Purba Medinipur','Medinipur'),
('Ramnagar',           'Purba Medinipur','Medinipur'),
('Egra',               'Purba Medinipur','Medinipur'),
('Dantan',             'Paschim Medinipur','Medinipur'),
('Nayagram',           'Paschim Medinipur','Medinipur'),
('Gopiballavpur',      'Jhargram',     'Medinipur'),
('Jhargram',           'Jhargram',     'Medinipur'),
('Keshiary',           'Paschim Medinipur','Medinipur'),
('Kharagpur Sadar',    'Paschim Medinipur','Medinipur'),
('Narayangarh',        'Paschim Medinipur','Medinipur'),
('Sabang',             'Paschim Medinipur','Medinipur'),
('Pingla',             'Paschim Medinipur','Medinipur'),
('Kharagpur',          'Paschim Medinipur','Medinipur'),
('Debra',              'Paschim Medinipur','Medinipur'),
('Daspur',             'Paschim Medinipur','Medinipur'),
('Ghatal',             'Paschim Medinipur','Medinipur'),
('Chandrakona',        'Paschim Medinipur','Medinipur'),
('Garbeta',            'Paschim Medinipur','Medinipur'),
('Salboni',            'Paschim Medinipur','Medinipur'),
('Keshpur',            'Paschim Medinipur','Medinipur'),
('Medinipur',          'Paschim Medinipur','Medinipur'),
('Binpur',             'Jhargram',     'Medinipur'),
('Bandwan',            'Purulia',      'Burdwan'),
('Balarampur',         'Purulia',      'Burdwan'),
('Baghmundi',          'Purulia',      'Burdwan'),
('Joypur',             'Purulia',      'Burdwan'),
('Purulia',            'Purulia',      'Burdwan'),
('Manbazar',           'Purulia',      'Burdwan'),
('Kashipur',           'Purulia',      'Burdwan'),
('Para',               'Purulia',      'Burdwan'),
('Raghunathpur',       'Purulia',      'Burdwan'),
('Saltora',            'Bankura',      'Burdwan'),
('Chhatna',            'Bankura',      'Burdwan'),
('Ranibandh',          'Bankura',      'Burdwan'),
('Raipur',             'Bankura',      'Burdwan'),
('Taldangra',          'Bankura',      'Burdwan'),
('Bankura',            'Bankura',      'Burdwan'),
('Barjora',            'Bankura',      'Burdwan'),
('Onda',               'Bankura',      'Burdwan'),
('Bishnupur',          'Bankura',      'Burdwan'),
('Katulpur',           'Bankura',      'Burdwan'),
('Indas',              'Bankura',      'Burdwan'),
('Sonamukhi',          'Bankura',      'Burdwan'),
('Pandabeswar',        'Paschim Bardhaman','Burdwan'),
('Durgapur Purba',     'Paschim Bardhaman','Burdwan'),
('Durgapur Paschim',   'Paschim Bardhaman','Burdwan'),
('Raniganj',           'Paschim Bardhaman','Burdwan'),
('Jamuria',            'Paschim Bardhaman','Burdwan'),
('Asansol Dakshin',    'Paschim Bardhaman','Burdwan'),
('Asansol Uttar',      'Paschim Bardhaman','Burdwan'),
('Kulti',              'Paschim Bardhaman','Burdwan'),
('Barabani',           'Paschim Bardhaman','Burdwan'),
('Dubrajpur',          'Birbhum',      'Burdwan'),
('Suri',               'Birbhum',      'Burdwan'),
('Bolpur',             'Birbhum',      'Burdwan'),
('Nanoor',             'Birbhum',      'Burdwan'),
('Labpur',             'Birbhum',      'Burdwan'),
('Sainthia',           'Birbhum',      'Burdwan'),
('Mayureswar',         'Birbhum',      'Burdwan'),
('Rampurhat',          'Birbhum',      'Burdwan'),
('Hansan',             'Birbhum',      'Burdwan'),
('Nalhati',            'Birbhum',      'Burdwan'),
('Murarai',            'Birbhum',      'Burdwan')
ON CONFLICT (ac_name) DO NOTHING;

-- ──────────────────────────────────────────────────────────
-- VIEWS for dashboard queries
-- ──────────────────────────────────────────────────────────

-- AC-level summary view
CREATE OR REPLACE VIEW ac_summary AS
SELECT
    ac_name,
    COUNT(*)                                              AS total_items,
    COUNT(*) FILTER (WHERE party_tag = 'TMC')            AS tmc_count,
    COUNT(*) FILTER (WHERE party_tag = 'BJP')            AS bjp_count,
    COUNT(*) FILTER (WHERE party_tag = 'Others')         AS others_count,
    COUNT(*) FILTER (WHERE sentiment = 'Positive')       AS positive_count,
    COUNT(*) FILTER (WHERE sentiment = 'Negative')       AS negative_count,
    COUNT(*) FILTER (WHERE sentiment = 'Neutral')        AS neutral_count,
    AVG(sentiment_score)                                  AS avg_sentiment,
    MAX(timestamp)                                        AS last_updated
FROM news_items
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY ac_name;

-- Hourly trend view
CREATE OR REPLACE VIEW hourly_trends AS
SELECT
    date_trunc('hour', timestamp)   AS hour_bucket,
    ac_name,
    party_tag,
    sentiment,
    COUNT(*)                         AS item_count
FROM news_items
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY 1, 2, 3, 4
ORDER BY 1 DESC;
