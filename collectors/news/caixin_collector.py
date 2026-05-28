import requests
from bs4 import BeautifulSoup
from datetime import datetime

CAIXIN_URL = "https://www.caixin.com/"  # 财新首页
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_caixin_news(limit=20):
    items = []
    try:
        resp = requests.get(CAIXIN_URL, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        news_list = soup.select("div.newsList li a")[:limit]
        for n in news_list:
            title = n.get_text(strip=True)
            link = n.get("href")
            pub_date = datetime.utcnow()
            items.append({
                "source": "财新网",
                "country": "CN",
                "title": title,
                "link": link,
                "date": pub_date
            })
    except Exception as e:
        print(f"Caixin News ERROR: {e}")
    return items