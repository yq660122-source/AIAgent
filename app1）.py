import os
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# ======================
# 页面设置
# ======================
st.set_page_config(
    page_title="AI FINANCIAL INTELLIGENCE SYSTEM",
    layout="wide"
)

st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ======================
# 顶部导航
# ======================
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.link_button(
        "📈 打开市场趋势分析",
        "http://localhost:8501/Market_Trend",
        use_container_width=True
    )

with nav_col2:
    st.link_button(
        "🌍 全球风险监控（开发中）",
        "http://localhost:8501",
        use_container_width=True
    )

with nav_col3:
    st.link_button(
        "🤖 AI宏观分析（开发中）",
        "http://localhost:8501",
        use_container_width=True
    )

# ======================
# API KEY
# ======================
FRED_API_KEY = os.getenv("FRED_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# ======================
# RSS 新闻源
# ======================
RSS_FEEDS = {
    "US Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB": "https://www.ecb.europa.eu/rss/press.xml"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ======================
# 市场指标
# ======================
FRED_SERIES = {
    "S&P 500": "SP500",
    "US 10Y Treasury (%)": "DGS10",
    "黄金 (USD/oz)": "GOLDAMGBD228NLBM",
    "WTI 原油 (USD/barrel)": "DCOILWTICO",
    "USD/CNY": "DEXCHUS"
}

# ======================
# 新闻抓取
# ======================
def fetch_rss(url, country):

    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        resp.raise_for_status()

        root = ET.fromstring(resp.content)

        items = []

        for i in root.findall(".//item")[:20]:

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

            items.append({
                "country": country,
                "title": title,
                "link": link,
                "date": pub_date
            })

        return items

    except Exception as e:

        st.warning(f"{country} 新闻抓取失败: {e}")

        return []

# ======================
# DeepSeek模拟分析（当前免费阶段）
# ======================
def fake_ai_analysis(news_title):

    title_lower = news_title.lower()

    summary = f"""
【中文翻译】
{news_title}

【市场解读】
该新闻可能对全球金融市场产生影响。
"""

    risk_score = 3
    trend = "中性"

    # 简单关键词逻辑
    if "inflation" in title_lower:
        risk_score = 7
        trend = "偏空"

        summary += """
通胀相关消息通常意味着：
- 美联储可能维持高利率
- 美股承压
- 黄金波动加剧
"""

    elif "rate" in title_lower:
        risk_score = 8
        trend = "高波动"

        summary += """
利率相关消息可能影响：
- 美债收益率
- 美元指数
- 全球风险资产
"""

    elif "growth" in title_lower:
        risk_score = 4
        trend = "偏多"

        summary += """
经济增长相关消息通常利好：
- 股票市场
- 风险偏好
"""

    return {
        "summary": summary,
        "risk_score": risk_score,
        "trend": trend
    }

# ======================
# FRED数据抓取
# ======================
def get_fred_latest(series_id):

    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}"
        f"&api_key={FRED_API_KEY}"
        f"&file_type=json"
        f"&sort_order=desc"
        f"&limit=30"
    )

    try:

        resp = requests.get(
            url,
            timeout=20
        ).json()

        obs = [
            o for o in resp.get("observations", [])
            if o["value"] != "."
        ]

        if not obs:
            return None, None, [], None

        history = [
            (o["date"], float(o["value"]))
            for o in obs
        ]

        history.reverse()

        fetch_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            obs[0]["date"],
            float(obs[0]["value"]),
            history,
            fetch_time
        )

    except:
        return None, None, [], None

# ======================
# 刷新按钮
# ======================
if st.button("🔄 刷新数据"):

    st.session_state.clear()

    st.success("缓存已清空，重新加载最新数据")

# ======================
# 新闻数据
# ======================
if "all_news" not in st.session_state:

    news = []

    for country, url in RSS_FEEDS.items():

        news += fetch_rss(url, country)

    # 时间排序
    news.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    st.session_state["all_news"] = news

else:

    news = st.session_state["all_news"]

news_df = pd.DataFrame(news)

# ======================
# 指标数据
# ======================
if "indicator_data" not in st.session_state:

    indicator_data = []
    history_dict = {}

    for name, series_id in FRED_SERIES.items():

        date, value, history, fetch_time = get_fred_latest(series_id)

        if value is not None:

            indicator_data.append({
                "指标": name,
                "最新值": value,
                "数据日期": date,
                "抓取时间": fetch_time
            })

            history_dict[name] = history

    st.session_state["indicator_data"] = indicator_data
    st.session_state["history_dict"] = history_dict

else:

    indicator_data = st.session_state["indicator_data"]
    history_dict = st.session_state["history_dict"]

indicator_df = pd.DataFrame(indicator_data)

# ======================
# 页面布局
# ======================
col1, col2 = st.columns([3, 1])

# ======================
# 新闻区
# ======================
with col1:

    st.subheader("📢 最新央行新闻")

    if not news_df.empty:

        for idx, row in news_df.iterrows():

            st.markdown(
                f"""
### [{row['title']}]({row['link']})

🌍 来源：{row['country']}

🕒 发布时间：{row['date'].strftime('%Y-%m-%d %H:%M:%S')}
"""
            )

            # 分析按钮
            button_key = f"analyze_{idx}"

            if st.button(
                f"🤖 DeepSeek深度分析 #{idx+1}",
                key=button_key
            ):

                analysis = fake_ai_analysis(
                    row["title"]
                )

                st.info(analysis["summary"])

                st.metric(
                    "风险评分",
                    analysis["risk_score"]
                )

                st.write(
                    f"市场趋势：{analysis['trend']}"
                )

            st.markdown("---")

    else:

        st.write("暂无新闻")

# ======================
# 指标区
# ======================
with col2:

    st.subheader("📊 市场指标")

    if not indicator_df.empty:

        for idx, row in indicator_df.iterrows():

            hist = history_dict.get(
                row["指标"],
                []
            )

            if hist and len(hist) > 1:

                change = (
                    (hist[-1][1] - hist[0][1])
                    / hist[0][1]
                ) * 100

                st.metric(
                    label=row["指标"],
                    value=f"{row['最新值']:.2f}",
                    delta=f"{change:.2f}%"
                )

            else:

                st.metric(
                    label=row["指标"],
                    value=f"{row['最新值']:.2f}"
                )

            st.caption(
                f"""
数据日期：
{row['数据日期']}

抓取时间：
{row['抓取时间']}
"""
            )

            st.markdown("---")

    else:

        st.write("暂无指标数据")

# ======================
# 首页只显示按钮
# 不再显示巨大趋势图
# ======================
st.subheader("📈 市场趋势分析")

st.info(
    """
点击顶部：
【📈 打开市场趋势分析】

将在新窗口打开专业趋势分析页面。
"""
)