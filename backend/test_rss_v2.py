import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": UA}

urls = [
    "https://bengali.news18.com/rss/west-bengal.xml",
    "https://bengali.oneindia.com/rss/bengali-news-fb.xml",
    "https://timesofindia.indiatimes.com/rssfeeds/2128936835.cms",
    "https://www.sangbadpratidin.in/feed/"
]

for url in urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"{url} -> {r.status_code}")
    except Exception as e:
        print(f"{url} -> Error: {e}")
