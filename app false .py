# app.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from collectors.news.chinanews_collector import fetch_chinanews
from collectors.news.fed_collector import fetch_fed_news
from collectors.news.ecb_collector import fetch_ecb_news
from collectors.market.fred_api import get_fred_latest
from collectors.market.alpha_vantage import get_realtime_price
from engines.news_tagging import tag_news
from engines.global_risk import calculate_global_risk
from engines.risk_engine import calculate_risk_score, get_risk_level
from engines.market_state import get_market_state
from ai.fake_ai import fake_ai_analysis
from utils.translator import translate_title

# ======================
# 页面配置
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
    st.button("📈 打开市场趋势分析", key="nav_market", help="新窗口打开", on_click=lambda: st.experimental_set_query_params(page="market_trend"))
with nav_col2:
    st.button("🌍 全球风险监控（开发中）", key="nav_risk")
with nav_col3:
    st.button("🤖 AI宏观分析（开发中）", key="nav_ai")

# ======================
# API KEY
# ======================
FRED_API_KEY = os.getenv("FRED_API_KEY")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

# ======================
# 数据刷新按钮
# ======================
if st.button("🔄 刷新数据"):
    st.session_state.clear()
    st.experimental_rerun()

# ======================
# 新闻抓取
# ======================
if "all_news" not in st.session_state:
    news = []
    try:
        cn_news = fetch_chinanews(limit=20)
        if cn_news:
            news.extend(cn_news)
        else:
            st.warning("⚠️ CN 新闻抓取失败或无数据")
    except Exception as e:
        st.warning(f"CN 新闻抓取异常: {e}")

    try:
        us_news = fetch_fed_news(limit=20)
        if us_news:
            news.extend(us_news)
    except Exception as e:
        st.warning(f"US 新闻抓取异常: {e}")

    try:
        eu_news = fetch_ecb_news(limit=20)
        if eu_news:
            news.extend(eu_news)
    except Exception as e:
        st.warning(f"EU 新闻抓取异常: {e}")

    # 按时间排序
    news.sort(key=lambda x: x["date"], reverse=True)
    st.session_state["all_news"] = news
else:
    news = st.session_state["all_news"]

# 新闻 DataFrame
news_df = pd.DataFrame(news)

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

REALTIME_SYMBOLS = {
    "SPY": "SPY",
    "黄金ETF": "GLD",
    "原油ETF": "USO",
    "比特币": "IBIT"
}

# ======================
# 市场指标数据
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
# 实时行情
# ======================
realtime_data = []
for name, symbol in REALTIME_SYMBOLS.items():
    data = get_realtime_price(symbol)
    if data:
        realtime_data.append({
            "name": name,
            "symbol": symbol,
            "price": data["price"],
            "change_percent": data["change_percent"]
        })

# ======================
# 首页布局
# ======================
col_news, col_market = st.columns([3, 1])

# ----------------------
# 新闻区域（滑动显示、分区 CN/US/EU）
# ----------------------
with col_news:
    st.subheader("📰 最新金融新闻（上下滑动）")

    country_order = ["CN", "US", "EU"]
    grouped_news = {c: [] for c in country_order}

    for _, row in news_df.iterrows():
        c = row.get("country", "Global")
        if c in grouped_news:
            grouped_news[c].append(row)

    for c in country_order:
        items = grouped_news[c]
        if items:
            st.markdown(f"### 🌍 {c}")
            for idx, row in enumerate(items):
                # 标题翻译
                title_data = translate_title(row["title"])

                # 风险标签
                tags = tag_news(row["title"]).get("tags", [])
                try:
                    risk_score = calculate_risk_score(row["title"], tags)
                    risk_level = get_risk_level(risk_score)
                except Exception:
                    risk_score = None
                    risk_level = None

                trend = get_market_state(risk_score)

                # 新闻展示
                st.markdown(
                    f"""
**[{row['source']}]** {title_data['original']}  
【中】{title_data['translated']}  
🕒 {row['date'].strftime('%Y-%m-%d %H:%M:%S')} | 🌍 {c} | [原文]({row['link']})
"""
                )

                # 风险预警
                if risk_score is not None:
                    st.info(f"风险评分: {risk_score} | 风险等级: {risk_level} | 趋势: {trend}")

                # AI分析折叠
                with st.expander(f"🤖 AI深度分析 #{c}-{idx+1}"):
                    analysis = fake_ai_analysis(row["title"])
                    st.write(analysis)

                st.markdown("---")
        else:
            st.write(f"⚠️ {c} 新闻暂无数据")

# ----------------------
# 实时市场 + 市场指标
# ----------------------
with col_market:
    st.subheader("⚡ 实时市场")
    for item in realtime_data:
        st.metric(label=item["name"], value=f"{item['price']:.2f}", delta=item["change_percent"])

    st.markdown("---")

    st.subheader("📊 市场指标")
    if not indicator_df.empty:
        for idx, row in indicator_df.iterrows():
            hist = history_dict.get(row["指标"], [])
            if hist and len(hist) > 1:
                change = (hist[-1][1] - hist[0][1]) / hist[0][1] * 100
                st.metric(label=row["指标"], value=f"{row['最新值']:.2f}", delta=f"{change:.2f}%")
            else:
                st.metric(label=row["指标"], value=f"{row['最新值']:.2f}")
            st.caption(f"数据日期：{row['数据日期']}\n抓取时间：{row['抓取时间']}")
            st.markdown("---")

# ----------------------
# 市场趋势导航提示
# ----------------------
st.subheader("📈 市场趋势分析")
st.info("点击顶部导航【📈 打开市场趋势分析】在新窗口打开专业趋势分析页面。")