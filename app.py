import os
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ======================
# 页面设置
# ======================
st.set_page_config(page_title="AI FINANCIAL INTELLIGENCE SYSTEM", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ======================
# 配置
# ======================
FRED_API_KEY = os.getenv("2bac9607b4b2e991e610838fae24637c")
DEEPSEEK_API_KEY = os.getenv("sk-175cd729d88249309c7f64c06e886ab1")

RSS_FEEDS = {
    "US Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB": "https://www.ecb.europa.eu/rss/press.xml"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

FRED_SERIES = {
    "S&P 500": "SP500",
    "US 10Y Treasury (%)": "DGS10",
    "黄金 (USD/oz)": "GOLDAMGBD228NLBM",
    "WTI 原油 (USD/barrel)": "DCOILWTICO",
    "USD/CNY": "DEXCHUS"
}

# ======================
# 新闻抓取函数（稳定版）
# ======================
def fetch_rss(url, country):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for i in root.findall(".//item")[:20]:  # 最新20条新闻
            title = i.find("title").text
            link = i.find("link").text
            pub_date_str = i.find("pubDate").text
            try:
                pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
            except:
                pub_date = datetime.utcnow()
            items.append({"country": country, "title": title, "link": link, "date": pub_date})
        if not items:
            st.warning(f"{country} 新闻抓取成功，但无新闻数据")
        return items
    except Exception as e:
        st.warning(f"{country} 新闻抓取失败: {e}")
        return []

# ======================
# DeepSeek 实时分析
# ======================
def analyze_with_deepseek(text):
    url = "https://api.deepseek.com/analyze"  # 示例URL，请替换成实际URL
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text, "options": {"tasks":["summary","risk_score","trend"]}}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return {
            "summary": data.get("summary","分析失败"),
            "risk_score": data.get("risk_score",0),
            "trend": data.get("trend","中性")
        }
    except:
        return {"summary":"分析失败", "risk_score":0, "trend":"中性"}

# ======================
# FRED 指标抓取函数（稳定版）
# ======================
def get_fred_latest(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=30"
    try:
        resp = requests.get(url, timeout=20).json()
        obs = [o for o in resp.get("observations", []) if o["value"] != "."]
        if not obs:
            return None, None, []
        history = [(o["date"], float(o["value"])) for o in obs]
        history.reverse()
        return obs[0]["date"], float(obs[0]["value"]), history
    except:
        return None, None, []

# ======================
# 刷新按钮
# ======================
if st.button("刷新数据"):
    st.session_state.clear()
    st.write("缓存已清空，重新加载最新数据")

# ======================
# 新闻数据
# ======================
if "all_news" not in st.session_state:
    news = []
    for country, url in RSS_FEEDS.items():
        news += fetch_rss(url, country)
    news.sort(key=lambda x: x["date"], reverse=True)
    for n in news:
        analysis = analyze_with_deepseek(n["title"])
        n.update(analysis)
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
# 页面布局
# ======================
col1, col2 = st.columns([3,1])

# 左侧新闻
with col1:
    st.subheader("📢 最新央行新闻（稳定版）")
    if not news_df.empty:
        for idx, row in news_df.iterrows():
            st.markdown(f"**[{row['title']}]({row['link']})** - {row['country']} ({row['date']:%Y-%m-%d %H:%M})")
            st.markdown(f"摘要: {row['summary']}")
            st.markdown(f"风险评分: {row['risk_score']}, 趋势: {row['trend']}")
            st.markdown("---")
    else:
        st.write("暂无新闻")

# 右侧指标 + metric
with col2:
    st.subheader("📊 市场指标")
    if not indicator_df.empty:
        for idx, row in indicator_df.iterrows():
            hist = history_dict.get(row["指标"], [])
            if hist and len(hist)>1:
                change = (hist[-1][1]-hist[0][1])/hist[0][1]*100
                st.metric(label=row["指标"], value=f"{row['最新值']:.2f}", delta=f"{change:.2f}%")
            else:
                st.metric(label=row["指标"], value=f"{row['最新值']:.2f}")
    else:
        st.write("暂无指标数据")

# ======================
# 单指标折线图
# ======================
st.subheader("📈 单指标趋势图")
for name, hist in history_dict.items():
    if hist:
        df = pd.DataFrame(hist, columns=["Date","Value"])
        df["Date"] = pd.to_datetime(df["Date"])
        st.subheader(name)
        st.line_chart(df.set_index("Date"))

# ======================
# 双轴趋势图
# ======================
st.subheader("📈 双轴趋势图（整体趋势对比）")
fig = go.Figure()
for name, hist in history_dict.items():
    if hist:
        df = pd.DataFrame(hist, columns=["Date","Value"])
        df["Date"] = pd.to_datetime(df["Date"])
        if name in ["S&P 500","US 10Y Treasury (%)"]:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["Value"], mode='lines', name=name, yaxis='y1'))
        else:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["Value"], mode='lines', name=name, yaxis='y2'))

fig.update_layout(
    xaxis_title="日期",
    yaxis=dict(title="S&P500 / US10Y", side="left"),
    yaxis2=dict(title="商品 / 汇率", overlaying='y', side='right'),
    legend_title="指标",
    hovermode="x unified"
)