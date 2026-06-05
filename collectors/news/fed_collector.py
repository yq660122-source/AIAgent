import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from models.intelligence_object import IntelligenceObject
from utils.safe_request import safe_get


FED_URL = "https://www.federalreserve.gov/feeds/press_all.xml"


def fetch_fed_news(limit=20):

    try:

        print(
            f"🐾 [FED] 开始请求美联储新闻 RSS: {FED_URL}"
        )

        resp = safe_get(FED_URL)

        if not resp:

            print(
                "⚠️ [FED] 请求失败，safe_get 返回空结果"
            )

            return []

        root = ET.fromstring(
            resp.content
        )

        items = []

        all_parsed_items = []

        for i in root.findall(".//item"):

            try:

                title = (
                    i.find("title").text
                    if i.find("title") is not None
                    else "No Title"
                )

                link = (
                    i.find("link").text
                    if i.find("link") is not None
                    else ""
                )

                pub_date_str = (
                    i.find("pubDate").text
                    if i.find("pubDate") is not None
                    else ""
                )

                try:

                    pub_date = datetime.strptime(
                        pub_date_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )

                except Exception:

                    pub_date = datetime.utcnow()

                obj = IntelligenceObject(

                    title=title,

                    content=title,

                    source="Federal Reserve",

                    category="CENTRAL_BANK",

                    region="US",

                    url=link,

                    event_type="FED"

                )

                data = obj.to_dict()

                # ======================
                # 兼容旧系统
                # ======================

                data["date"] = pub_date

                data["country"] = "US"

                data["link"] = link

                # ======================
                # 历史池
                # ======================

                all_parsed_items.append(
                    data
                )

                # ======================
                # 48小时内新闻
                # ======================

                if (

                    datetime.utcnow()
                    - pub_date

                    <= timedelta(hours=48)

                ):

                    items.append(
                        data
                    )

                    if len(items) >= limit:

                        break

            except Exception as inner_e:

                print(
                    f"⚠️ [FED ITEM ERROR]: {inner_e}"
                )

                continue

        print(

            f"🐾 [FED] 抓取完成。"

            f"48小时内新闻: {len(items)} 条，"

            f"历史池: {len(all_parsed_items)} 条"

        )

        # ======================
        # Fallback
        # ======================

        if (

            not items

            and

            all_parsed_items

        ):

            print(
                "💡 [FED Fallback] 启动历史新闻兜底"
            )

            all_parsed_items.sort(

                key=lambda x: x["date"],

                reverse=True

            )

            items = all_parsed_items[:5]

        return items

    except Exception as e:

        print(
            f"💥 [FED NEWS ERROR]: {e}"
        )

        return []