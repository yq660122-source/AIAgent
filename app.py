import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# ======================
# 页面设置
# ======================
st.set_page_config(page_title="AI FINANCIAL INTELLIGENCE SYSTEM", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ======================
# API KEY
# ======================
FRED_API_KEY = "你的FRED_API_KEY"

# ======================
# 新闻抓取
# ======================
def fetch_rss(url, country_name):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            st.warning(f"{country_name} RSS 响应状态码不是200: {resp.status_code}")
            return []
        root = ET.fromstring(resp.content)
        news_items = []
        for item in root.findall(".//item")[:10]:
            title = item.find("title").text
            link = item.find("link").text
            pub_date = item.find("pubDate").text
            news_items.append({
                "country": country_name,
                "title": title,
                "link": link,
                "date": pub_date
            })
        return news_items
    except Exception as e:
        st.warning(f"抓取 {country_name} 新闻失败: {e}")
        return []

rss_feeds = {
    "US Fed": "https://www.federalreserve.gov/feeds/press_all.xml"
}

all_news = []
for country, url in rss_feeds.items():
    all_news += fetch_rss(url, country)

news_df = pd.DataFrame(all_news)

# ======================
# FRED 数据抓取
# ======================
def get_fred_latest(series_id):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={FRED_API_KEY}"
        f"&file_type=json&sort_order=desc&limit=30"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "observations" not in data:
            st.error(f"{series_id} 数据获取失败")
            return None, None, []
        observations = data["observations"]
        valid_obs = [obs for obs in observations if obs["value"] != "."]
        if len(valid_obs) == 0:
            st.error(f"{series_id} 没有有效数据")
            return None, None, []
        value = float(valid_obs[0]["value"])
        date = valid_obs[0]["date"]
        history = [(obs["date"], float(obs["value"])) for obs in valid_obs]
        history.reverse()
        return date, value, history
    except Exception as e:
        st.error(f"{series_id} 获取失败: {e}")
        return None, None, []

# ======================
# 获取指标
# ======================
indicator_data = []

# S&P500
sp_date, sp_value, sp_history = get_fred_latest("SP500")
if sp_value is not None:
    indicator_data.append({"指标": "S&P 500", "最新值": sp_value, "日期": sp_date})

# US 10Y Treasury
tnx_date, tnx_value, tnx_history = get_fred_latest("DGS10")
if tnx_value is not None:
    indicator_data.append({"指标": "US 10Y Treasury (%)", "最新值": tnx_value, "日期": tnx_date})

indicator_df = pd.DataFrame(indicator_data)

# ======================
# 页面布局
# ======================
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📢 最新央行新闻")
    if not news_df.empty:
        st.dataframe(news_df[["country", "title", "link", "date"]], use_container_width=True)
    else:
        st.write("暂无新闻数据")

with col2:
    st.subheader("📊 市场指标")
    if not indicator_df.empty:
        st.dataframe(indicator_df, use_container_width=True)
    else:
        st.write("暂无指标数据")

# ======================
# 趋势图（Streamlit 内置）
# ======================
st.subheader("📈 指标趋势图")

def plot_trend(history, title):
    if len(history) == 0:
        return
    df = pd.DataFrame(history, columns=["Date", "Value"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    st.write(title)
    st.line_chart(df)

plot_trend(sp_history, "S&P 500")
plot_trend(tnx_history, "US 10Y Treasury (%)")

# ======================
# AI 分析占位
# ======================
st