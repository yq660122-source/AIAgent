import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="AI FINANCIAL INTELLIGENCE SYSTEM", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ======================
# 1️⃣ 新闻抓取（美联储 RSS）
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
# 2️⃣ 金融市场指标（FRED + Alpha Vantage）
# ======================
st.subheader("📊 关键市场指标")

# ---- FRED API 设置 ----
FRED_API_KEY = "2bac9607b4b2e991e610838fae24637c"

def get_fred_latest(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=30"
    resp = requests.get(url)
    data = resp.json()
    # 返回最新值和日期
    value = float(data["observations"][0]["value"])
    date = data["observations"][0]["date"]
    # 历史数据用于趋势图
    history = [(obs["date"], float(obs["value"])) for obs in data["observations"] if obs["value"] != '.']
    history.reverse()  # 日期正序
    return date, value, history

# ---- Alpha Vantage API 设置 ----
ALPHA_KEY = "9KHASSZJY063QAT8"

def get_alpha_currency(symbol="USDCNY"):
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=CNY&apikey={ALPHA_KEY}"
    resp = requests.get(url).json()
    rate = float(resp["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    return rate

def get_alpha_commodity(symbol="GC=F"):
    # 黄金或原油，使用 TIME_SERIES_DAILY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_KEY}"
    resp = requests.get(url).json()
    ts = resp.get("Time Series (Daily)", {})
    dates = sorted(ts.keys())
    latest_date = dates[-1]
    latest_value = float(ts[latest_date]["4. close"])
    history = [(d, float(ts[d]["4. close"])) for d in dates]
    history.reverse()
    return latest_date, latest_value, history

# ---- 获取指标 ----
indicator_data = []

# S&P500
sp_date, sp_value, sp_history = get_fred_latest("SP500")
indicator_data.append({"指标": "S&P 500", "最新值": sp_value, "日期": sp_date})

# 10Y Treasury
tnx_date, tnx_value, tnx_history = get_fred_latest("DGS10")
indicator_data.append({"指标": "US 10Y Treasury (%)", "最新值": tnx_value, "日期": tnx_date})

# USD/CNY
usd_cny = get_alpha_currency()
indicator_data.append({"指标": "USD/CNY", "最新值": usd_cny, "日期": datetime.today().strftime("%Y-%m-%d")})

# 黄金
gold_date, gold_value, gold_history = get_alpha_commodity("GC=F")
indicator_data.append({"指标": "Gold (USD/oz)", "最新值": gold_value, "日期": gold_date})

# 原油
oil_date, oil_value, oil_history = get_alpha_commodity("CL=F")
indicator_data.append({"指标": "Crude Oil WTI (USD/bbl)", "最新值": oil_value, "日期": oil_date})

indicator_df = pd.DataFrame(indicator_data)

# ======================
# 3️⃣ 网页布局
# ======================
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

# ======================
# 4️⃣ 趋势图展示
# ======================
st.subheader("📈 指标趋势图")

def plot_trend(history, title):
    df = pd.DataFrame(history, columns=["Date", "Value"])
    df["Date"] = pd.to_datetime(df["Date"])
    plt.figure(figsize=(6,3))
    plt.plot(df["Date"], df["Value"], marker='o')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.image(buf)

# 显示趋势图
plot_trend(sp_history, "S&P 500")
plot_trend(tnx_history, "US 10Y Treasury (%)")
plot_trend(gold_history, "Gold (USD/oz)")
plot_trend(oil_history, "Crude Oil WTI (USD/bbl)")

# ======================
# 5️⃣ AI 分析接口占位
# ======================
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

# ======================
# 6️⃣ 刷新按钮
# ======================
if st.button("刷新数据"):
    st.experimental_rerun()