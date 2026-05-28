import requests
from bs4 import BeautifulSoup
from datetime import datetime

XINHUANET_URL = "http://www.xinhuanet.com/finance/"  # 财经首页
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_xinhua_news(limit=20):
    items = []
    try:
        resp = requests.get(XINHUANET_URL, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        news_list = soup.select("div.dataList li a")[:limit]
        for n in news_list:
            title = n.get_text(strip=True)
            link = n.get("href")
            pub_date = datetime.utcnow()  # 网页没时间可用时，使用当前时间
            items.append({
                "source": "新华网",
                "country": "CN",
                "title": title,
                "link": link,
                "date": pub_date
            })
    except Exception as e:
        print(f"Xinhua News ERROR: {e}")
    return items