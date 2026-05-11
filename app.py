import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# ======================
# 1. 页面设置
# ======================
st.set_page_config(page_title="AI FINANCIAL INTELLIGENCE SYSTEM", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ======================
# 2. 配置
# ======================
FRED_API_KEY = "2bac9607b4b2e991e610838fae24637c"

# 新闻源（稳定可用）
RSS_FEEDS = {
    "US Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB": "https://www.ecb.europa.eu/rss/press.xml"
}

KEYWORDS = ["战争", "疫情", "能源", "利率", "政策"]

# 市场指标（FRED 系列）
FRED_SERIES = {
    "S&P 500": "SP500",
    "US 10Y Treasury (%)": "DGS10",
    "黄金 (USD/oz)": "GOLDAMGBD228NLBM",
    "WTI 原油 (USD/barrel)": "DCOILWTICO",
    "USD/CNY": "DEXCHUS"
}

# ======================
# 3. 新闻抓取函数
# ======================
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"}

def fetch_rss_filtered(url, country):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for i in root.findall(".//item")[:15]:
            title = i.find("title").text
            link = i.find("link").text
            pub_date = i.find("pubDate").text
            if any(k in title for k in KEYWORDS):
                items.append({"country": country, "title": title, "link": link, "date": pub_date})
        if not items:
            st.warning(f"{country} 新闻抓取成功，但无匹配关键词新闻")
        return items
    except Exception as e:
        st.warning(f"{country} 新闻抓取失败: {e}")
        return []

# ======================
# 4. FRED 指标抓取函数
# ======================
def get_fred_latest(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=30"
    try:
        resp = requests.get(url, timeout=10).json()
        obs = [o for o in resp.get("observations", []) if o["value"] != "."]
        if not obs: return None, None, []
        history = [(o["date"], float(o["value"])) for o in obs]
        history.reverse()
        return obs[0]["date"], float(obs[0]["value"]), history
    except Exception as e:
        st.error(f"{series_id} 抓取失败: {e}")
        return None, None, []

# ======================
# 5. 刷新按钮
# ======================
if st.button("刷新数据"):
    st.session_state.clear()
    st.write("数据已清空，请刷新浏览器重新加载最新数据")

# ======================
# 6. 新闻数据处理
# ======================
if "all_news" not in st.session_state:
    news = []
    for country, url in RSS_FEEDS.items():
        news += fetch_rss_filtered(url, country)
    st.session_state["all_news"] = news
else:
    news = st.session_state["all_news"]

news_df = pd.DataFrame(news)

# ======================
# 7. 指标数据处理
# ======================
if "indicator_data" not in st.session_state:
    indicator_data = []
    history_dict = {}
    for name, series_id in FRED_SERIES.items():
        date, value, history = get_fred_latest(series_id)
        if value is not None:
            indicator_data.append({"指标": name, "最新值": value, "日期": date})
            history_dict[name] = history
    st.session_state["indicator_data"] = indicator_data
    st.session_state["history_dict"] = history_dict
else:
    indicator_data = st.session_state["indicator_data"]
    history_dict = st.session_state["history_dict"]

indicator_df = pd.DataFrame(indicator_data)

# ======================
# 8. 页面布局
# ======================
col1, col2 = st.columns([3,1])

with col1:
    st.subheader("📢 最新央行新闻")
    if not news_df.empty:
        for idx, row in news_df.iterrows():
            st.markdown(f"[{row['title']}]({row['link']}) - {row['country']} ({row['date']})")
    else:
        st.write("暂无新闻数据")

with col2:
    st.subheader("📊 市场指标")
    if not indicator_df.empty:
        st.dataframe(indicator_df, use_container_width=True)
    else:
        st.write("暂无指标数据")

# ======================
# 9. 趋势图显示
# ======================
st.subheader("📈 指标趋势图")
for name, hist in history_dict.items():
    if hist:
        df = pd.DataFrame(hist, columns=["Date","Value"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        st.line_chart(df, height=250, use_container_width=True)

# ======================
# 10. AI分析占位
# ======================
st.subheader("🤖 AI 分析结果")
def analyze_news(news_list):
    result = {}
    countries = set(n["country"] for n in news_list)
    for c in countries:
        count = sum(1 for n in news_list if n["country"]==c)
        result[c] = {"新闻数量": count, "风险评分": round(count*0.1,2), "趋势":"中性"}
    return result

st.dataframe(analyze_news(news), use_container_width=True)