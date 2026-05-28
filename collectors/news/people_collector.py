import requests
import xml.etree.ElementTree as ET
from datetime import datetime

PEOPLE_URL = "http://finance.people.com.cn/GB/317119/index.xml"  # 假设官方RSS
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_people_news(limit=20):
    items = []
    try:
        resp = requests.get(PEOPLE_URL, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        for i, item in enumerate(root.findall(".//item")):
            if i >= limit:
                break
            title = item.find("title").text
            link = item.find("link").text
            pub_date_str = item.find("pubDate").text
            try:
                pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
            except:
                pub_date = datetime.utcnow()
            items.append({
                "source": "人民网",
                "country": "CN",
                "title": title,
                "link": link,
                "date": pub_date
            })
    except Exception as e:
        print(f"People News ERROR: {e}")
    return items