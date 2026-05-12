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
st.set_page_config(page_title="AI FINANCIAL INTELLIGENCE SYSTEM", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")

# ======================
# 配置
# ======================
FRED_API_KEY = os.getenv("FRED_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_FEEDS = {
    "US Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB": "https://www.ecb.europa.eu/rss/press.xml"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

FRED_SERIES = {
    "S&P 500": "SP500",
    "US 10Y Treasury (%)": "DGS10",
    "黄金 (USD/oz)": "GOLDAMGBD228NLBM",
    "WTI 原油 (USD/barrel)": "DCOILWTICO",
    "USD/CNY": "DEXCHUS"
}

# ======================
# 新闻抓取函数
# ======================
def fetch_rss(url, country):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for i in root.findall(".//item")[:20]:
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
# ======================
# AI 分析部分（DeepSeek 点击分析）
# ======================
st.subheader("🤖 AI 分析（点击按钮获取深度分析）")

# 确保 session_state 存储每条新闻的分析结果
if "news_analysis" not in st.session_state:
    st.session_state["news_analysis"] = {}

for idx, row in news_df.iterrows():
    news_id = f"news_{idx}"  # 每条新闻唯一标识
    st.markdown(f"**[{row['title']}]({row['link']})** - {row['country']} ({row['date']:%Y-%m-%d %H:%M})")
    
    # 检查是否已经分析过
    if news_id in st.session_state["news_analysis"]:
        analysis = st.session_state["news_analysis"][news_id]
        st.markdown(f"摘要: {analysis['summary']}")
        st.markdown(f"风险评分: {analysis['risk_score']}, 趋势: {analysis['trend']}")
    else:
        # 创建按钮
        if st.button(f"深度分析这条新闻", key=news_id):
            try:
                url = "https://api.deepseek.com/v1/news/analyze"  # 这里填你实际 DeepSeek 接口 URL
                headers = {
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": row['title'],
                    "model": "deepseek-v4-flash",
                    "options": {"tasks":["summary","risk_score","trend"], "system_prompt":"解读并分析该条新闻，要求专业贴合市场"}
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                analysis = {
                    "summary": data.get("summary","分析失败"),
                    "risk_score": data.get("risk_score",0),
                    "trend": data.get("trend","中性")
                }
            except:
                analysis = {"summary":"分析失败","risk_score":0,"trend":"中性"}
            
            # 保存到 session_state，刷新后仍保留
            st.session_state["news_analysis"][news_id] = analysis
            st.markdown(f"摘要: {analysis['summary']}")
            st.markdown(f"风险评分: {analysis['risk_score']}, 趋势: {analysis['trend']}")
    
    st.markdown("---")

# ======================
# FRED 指标抓取函数
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
    st.subheader("📢 最新央行新闻（前20条）")
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
st.plotly_chart(fig, use_container_width=True)