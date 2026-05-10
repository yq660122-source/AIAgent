import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AI FINANCIAL INTELLIGENCE SYSTEM", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ----------------------
# 1️⃣ 新闻抓取模块
# ----------------------
def fetch_rss(url, country_name):
    try:
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        news_items = []
        for item in root.findall(".//item")[:10]:  # 取前10条
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

# RSS 链接
rss_feeds = {
    "US Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB": "https://www.ecb.europa.eu/rss/press.xml",
    "BoE": "https://www.bankofengland.co.uk/-/media/boe/rss-feed.xml",
    "PBoC": "http://www.pbc.gov.cn/rss/rss.xml"  # 占位，可更新
}

all_news = []
for country, url in rss_feeds.items():
    all_news += fetch_rss(url, country)

news_df = pd.DataFrame(all_news)

# ----------------------
# 2️⃣ 金融市场指标
# ----------------------
st.subheader("📈 关键市场指标")

def fetch_yahoo_finance(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    try:
        resp = requests.get(url, timeout=10).json()
        quote = resp["quoteResponse"]["result"][0]
        return quote.get("regularMarketPrice"), quote.get("regularMarketChangePercent")
    except Exception as e:
        st.warning(f"抓取 {symbol} 数据失败: {e}")
        return None, None

# 指标
indicators = {
    "S&P 500": "^GSPC",
    "VIX": "^VIX",
    "US 10Y Treasury": "^TNX",
    "USD/CNY": "USDCNY=X",
    "Gold": "GC=F",
    "Crude Oil WTI": "CL=F"
}

indicator_data = []
for name, symbol in indicators.items():
    price, change = fetch_yahoo_finance(symbol)
    indicator_data.append({"指标": name, "最新值": price, "涨跌幅(%)": change})

indicator_df = pd.DataFrame(indicator_data)

# ----------------------
# 3️⃣ 网页布局
# ----------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📢 最新央行新闻")
    st.dataframe(news_df[["country", "title", "link", "date"]])

with col2:
    st.subheader("📊 市场指标")
    st.dataframe(indicator_df)

# ----------------------
# 4️⃣ AI 分析接口
# ----------------------
st.subheader("🤖 AI 分析结果")

def analyze_news(news_list):
    # 占位逻辑：统计新闻数量 + 简单风险评分
    result = {}
    for country in set(n["country"] for n in news_list):
        count = sum(1 for n in news_list if n["country"] == country)
        result[country] = {
            "新闻数量": count,
            "风险评分": round(count * 0.1, 2),
            "趋势": "中性"
        }
    return result

analysis_result = analyze_news(all_news)
st.json(analysis_result)

# ----------------------
# 5️⃣ 刷新按钮
# ----------------------
if st.button("刷新数据"):
    st.experimental_rerun()