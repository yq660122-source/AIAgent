import xml.etree.ElementTree as ET

from datetime import datetime, timedelta

from utils.safe_request import safe_get


ECB_URL = "https://www.ecb.europa.eu/rss/press.xml"


def fetch_ecb_news(limit=20):

    try:

        resp = safe_get(
            ECB_URL
        )

        if not resp:
            return []

        root = ET.fromstring(resp.content)

        items = []

        for i in root.findall(".//item"):

            try:

                title = i.find("title").text
                link = i.find("link").text

                pub_date_str = i.find("pubDate").text

                try:

                    pub_date = datetime.strptime(
                        pub_date_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )

                except:

                    pub_date = datetime.utcnow()

                # 只保留48小时内新闻
                if datetime.utcnow() - pub_date > timedelta(hours=48):
                    continue

                items.append({

                    "source": "ECB",

                    "country": "EU",

                    "title": title,

                    "link": link,

                    "date": pub_date

                })

                # 达到limit后停止
                if len(items) >= limit:
                    break

            except Exception as inner_e:

                print(f"ECB ITEM ERROR: {inner_e}")

                continue

        return items

    except Exception as e:

        print(f"ECB NEWS ERROR: {e}")

        return []
