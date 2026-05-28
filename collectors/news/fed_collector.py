import xml.etree.ElementTree as ET

from datetime import datetime, timedelta

from models.intelligence_object import IntelligenceObject

from utils.safe_request import safe_get


FED_URL = "https://www.federalreserve.gov/feeds/press_all.xml"


def fetch_fed_news(limit=20):

    try:

        resp = safe_get(
            FED_URL
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

                obj = IntelligenceObject(

                    title=title,

                    content=title,

                    source="Federal Reserve",

                    category="CENTRAL_BANK",

                    region="US",

                    url=link,

                    event_type="FED",

                )

                data = obj.to_dict()

                # 兼容旧系统
                data["date"] = pub_date
                data["country"] = "US"
                data["link"] = link

                items.append(data)

                # 达到limit后停止
                if len(items) >= limit:
                    break

            except Exception as inner_e:

                print(f"FED ITEM ERROR: {inner_e}")

                continue

        return items

    except Exception as e:

        print(f"FED NEWS ERROR: {e}")

        return []