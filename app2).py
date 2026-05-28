import os
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from collectors.market.fred_api import get_fred_latest
from collectors.news.fed_collector import fetch_fed_news
from collectors.news.ecb_collector import fetch_ecb_news
from ai.fake_ai import fake_ai_analysis
from collectors.market.alpha_vantage import (
    get_realtime_price
)
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
# Alpha 实时行情
# ======================

REALTIME_SYMBOLS = {

    "SPY": "SPY",

    "黄金ETF": "GLD",

    "原油ETF": "USO",

    "比特币": "IBIT"
}




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

    news += fetch_fed_news()

    news += fetch_ecb_news()

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

            "change_percent": data[
                "change_percent"
            ]
        })
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
    f"风险等级：{analysis['risk_level']}"
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

    # ======================
    # 实时市场
    # ======================

    st.subheader("⚡ 实时市场")

    for item in realtime_data:

        st.metric(

            label=item["name"],

            value=f"{item['price']:.2f}",

            delta=item["change_percent"]
        )

    st.markdown("---")

    # ======================
    # 市场指标
    # ======================

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