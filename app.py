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
from engines.market_state import (
calculate_market_state
)
from utils.translator import (
    translate_title
)
from engines.news_tagging import (
    tag_news
)
from engines.global_risk import (
    calculate_global_risk
)
from engines.risk_engine import (
    calculate_risk_score,
    get_risk_level
)
#--------------
from collectors.news.people_collector import fetch_people_news
from collectors.news.xinhuanet_collector import fetch_xinhua_news
from collectors.news.caixin_collector import fetch_caixin_news
#======================

#页面设置

#======================

st.set_page_config(
page_title="AI FINANCIAL INTELLIGENCE SYSTEM",
layout="wide"
)

st.title("AI FINANCIAL INTELLIGENCE SYSTEM 🚀")



#======================

#顶部导航

#======================
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    if st.button(
        "📈 打开市场趋势分析",
        use_container_width=True
    ):
        st.markdown(
            "[点击进入市场趋势页](http://localhost:8501/market_trend)"
        )

with nav_col2:
    st.button(
        "🌍 全球风险监控（开发中）",
        use_container_width=True
    )

with nav_col3:
    st.button(
        "🤖 AI宏观分析（开发中）",
        use_container_width=True
    )

#======================

#API KEY

#======================

FRED_API_KEY = os.getenv("FRED_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

#======================

#市场指标

#======================

FRED_SERIES = {
"S&P 500": "SP500",
"US 10Y Treasury (%)": "DGS10",
"黄金 (USD/oz)": "GOLDAMGBD228NLBM",
"WTI 原油 (USD/barrel)": "DCOILWTICO",
"USD/CNY": "DEXCHUS"
}

#======================

#Alpha 实时行情

#======================

REALTIME_SYMBOLS = {

"SPY": "SPY",  

"黄金ETF": "GLD",  

"原油ETF": "USO",  

"比特币": "IBIT"

}

#======================

#刷新按钮

#======================

if st.button("🔄 刷新数据"):

  st.session_state.clear()  

  st.success("缓存已清空，重新加载最新数据")

#======================

#新闻数据

#======================

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
# 全球风险统计
# ======================

global_risk = calculate_global_risk(
    news
)


#======================

# 指标数据

#======================

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

    indicator_data = st.session_state.get("indicator_data", [])
    history_dict = st.session_state.get("history_dict", {})

indicator_df = pd.DataFrame(indicator_data)



#======================

# 实时行情

#======================

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

#======================

# 市场状态引擎

#======================

spy_change = 0
treasury_change = 0
gold_change = 0

# SPY（实时）

for item in realtime_data:

    if item["name"] == "SPY":

        spy_change = float(
            item["change_percent"]
            .replace("%", "")
        )

# 美债（FRED）

hist = history_dict.get(
    "US 10Y Treasury (%)",
    []
)

if len(hist) > 1:

    treasury_change = (

        (hist[-1][1] - hist[0][1])

        / hist[0][1]

    ) * 100

# 黄金（FRED）

hist = history_dict.get(
    "黄金 (USD/oz)",
    []
)

if len(hist) > 1:

    gold_change = (

        (hist[-1][1] - hist[0][1])

        / hist[0][1]

    ) * 100

market_state = calculate_market_state(

    spy_change,

    treasury_change,

    gold_change

)

# ======================
# 市场状态
# ======================

st.success(

    f"""
🌍 MARKET STATE:

{market_state['state']}

{market_state['description']}
"""
)

# ======================
# 全球风险面板
# ======================

st.subheader("🌍 GLOBAL RISK DASHBOARD")

risk_cols = st.columns(5)

risk_items = list(global_risk.items())

for idx, (risk_name, score) in enumerate(risk_items):

    if score >= 6:

        level = "🔴 HIGH"

    elif score >= 3:

        level = "🟠 MEDIUM"

    else:

        level = "🟢 LOW"

    with risk_cols[idx]:

        st.metric(

            label=risk_name,

            value=level,

            delta=f"Score: {score}"

        )

# ======================
# 新闻抓取
# ======================

# ---------- 中国新闻 ----------

cn_news = []


# ---------- 美国新闻 ----------

us_news = fetch_fed_news(limit=20)

# ---------- 欧洲新闻 ----------

eu_news = fetch_ecb_news(limit=20)

# ---------- 合并所有新闻 ----------

all_news = cn_news + us_news + eu_news

# ======================
# 新闻分组 + 排序
# ======================

from collections import OrderedDict

country_order = [

    "CN",

    "US",

    "EU",

    "UK",

    "JP",

    "Global"

]

grouped_news = {}

for item in all_news:

    country = item.get("country", "Global")

    if country not in grouped_news:

        grouped_news[country] = []

    grouped_news[country].append(item)

ordered_grouped_news = OrderedDict()

for c in country_order:

    if c in grouped_news:

        ordered_grouped_news[c] = grouped_news[c]

for c in grouped_news:

    if c not in ordered_grouped_news:

        ordered_grouped_news[c] = grouped_news[c]
# ======================
# 页面布局
# ======================
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📰 GLOBAL FINANCIAL NEWS")

    # ======================
    # 遍历各分组新闻
    # ======================
    for source, items in ordered_grouped_news.items():
        st.markdown(f"## 🌍 {source}")

        news_container = st.container()
        with news_container:
            for idx, row in enumerate(items):
                # ----------------------
                # 标题翻译
                # ----------------------

                title_data = translate_title(row["title"])

                # ----------------------
                # 风险标签
                # ----------------------
                tag_data = tag_news(row["title"])

                # ----------------------
                # 风险评分（Rule-based）
                # ----------------------
                risk_score = calculate_risk_score(row["title"], tag_data.get("tags", []))
                risk_level = get_risk_level(risk_score)

                # ----------------------
                # 趋势判断（兼容旧系统）
                # ----------------------
                if risk_score >= 80:
                    trend = "RISK OFF"
                elif risk_score >= 50:
                    trend = "VOLATILE"
                else:
                    trend = "NEUTRAL"

                # ----------------------
                # 新闻条目显示
                # ----------------------
                st.markdown(
                    f"""
<div style="
padding:8px;
border:1px solid #333;
border-radius:6px;
margin-bottom:8px;
">
<div style="
color:{tag_data.get('color','#000')};
font-weight:bold;
font-size:13px;
margin-bottom:4px;
">
{tag_data.get('icon','')}
{tag_data.get('tag','未分类')}
| Risk Score: {risk_score}
| Level: {risk_level}
</div>
<div style="
font-size:15px;
font-weight:600;
margin-bottom:4px;
">
{title_data['original']}
</div>
<div style="
color:#AAA;
font-size:13px;
">
【中】{title_data['translated']}
</div>
<div style="
color:#888;
font-size:12px;
">
🕒 {str(row['date'])}
| 🌍 {source}
| <a href="{row['link']}" target="_blank">原文</a>
</div>
</div>
                    """,
                    unsafe_allow_html=True
                )

                # ----------------------
                # AI分析折叠（暂不调用 AI，只保留接口）
                # ----------------------
                with st.expander(f"🤖 AI深度分析 #{source}-{idx+1}"):
                    st.info("AI分析暂未接入，可在未来直接启用 DeepSeek API")
                    # 以下为占位结构，未来替换 fake_ai_analysis 即可
                    # analysis = fake_ai_analysis(row["title"])
                    # st.info(analysis["summary"])
                    # st.metric("风险评分", analysis["risk_score"])
                    # st.write(f"风险等级：{analysis['risk_level']}")
                    # st.write(f"市场趋势：{analysis['trend']}")
# ======================
# 右侧指标区
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
            hist = history_dict.get(row["指标"], [])
            if hist and len(hist) > 1:
                change = ((hist[-1][1] - hist[0][1]) / hist[0][1]) * 100
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
# Footer Navigation
# ======================

st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:

    if st.button(
        "📈 市场趋势分析",
        use_container_width=True,
        key="footer_market_btn"
    ):
        st.markdown(
            "[点击进入市场趋势页](http://localhost:8501/market_trend)"
        )

with footer_col2:

    st.button(
        "🌍 风险监控（开发中）",
        use_container_width=True,
        key="footer_risk_btn"
    )

with footer_col3:

    st.button(
        "🤖 AI宏观分析（开发中）",
        use_container_width=True,
        key="footer_ai_btn"
    )