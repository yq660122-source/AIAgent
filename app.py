import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

st.set_page_config(page_title="AI FINANCIAL INTELLIGENCE SYSTEM", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ----------------------
# 1️⃣ 新闻抓取（只保留美联储，保证稳定）
# ----------------------
def fetch_rss(url, country_name):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            st.warning(f"{country_name} RSS 响应状态码不是200: {resp.status_code}")
            return []
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

rss_feeds = {
    "US Fed": "https://www.federalreserve.gov/feeds/press_all.xml"
}

all_news = []
for country, url in rss_feeds.items():
    all_news += fetch_rss(url, country)

news_df = pd.DataFrame(all_news)

# ----------------------
# 2️⃣ 金融市场指标（只保留 S&P500 和 VIX，保证稳定）
# ----------------------
st.subheader("📊 关键市场指标")

def fetch_yahoo_finance(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            st.warning(f"{symbol} 响应状态码不是200: {resp.status_code}")
            return None, None
        resp_json = resp.json()
        if "quoteResponse" not in resp_json or len(resp_json["quoteResponse"]["result"]) == 0:
            st.warning(f"{symbol} 返回数据为空")
            return None, None
        quote = resp_json["quoteResponse"]["result"][0]
        return quote.get("regularMarketPrice"), quote.get("regularMarketChangePercent")
    except Exception as e:
        st.warning(f"抓取 {symbol} 数据失败: {e}")
        return None, None

indicators = {
    "S&P 500": "^GSPC",
    "VIX": "^VIX"
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
    if not news_df.empty:
        st.dataframe(news_df[["country", "title", "link", "date"]])
    else:
        st.write("暂无新闻数据")

with col2:
    st.subheader("📊 市场指标")
    st.dataframe(indicator_df)

# ----------------------
# 4️⃣ AI 分析接口（占位）
# ----------------------
st.subheader("🤖 AI 分析结果")
def analyze_news(news_list):
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