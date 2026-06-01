import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from collectors.market.fred_api import get_fred_latest


# ======================
# 页面配置
# ======================

st.set_page_config(
    page_title="Market Trend Analysis",
    layout="wide"
)

st.title("📈 Market Trend Analysis")


# ======================
# 顶部导航
# ======================

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.button("🏠 返回首页", key="home_nav")

with nav_col2:
    st.button("🌍 全球风险监控", key="risk_nav")

with nav_col3:
    st.button("🤖 AI宏观分析", key="ai_nav")


# ======================
# FRED 市场指标
# ======================

st.subheader("📊 市场指标")

FRED_SERIES = {

    "S&P 500": "SP500",

    "US 10Y Treasury (%)": "DGS10",

    "黄金 (USD/oz)": "GOLDAMGBD228NLBM",

    "WTI 原油 (USD/barrel)": "DCOILWTICO",

    "USD/CNY": "DEXCHUS"

}

indicator_data = []

history_dict = {}


for name, series_id in FRED_SERIES.items():

    try:

        date, value, history, fetch_time = get_fred_latest(series_id)

        if value is not None:

            indicator_data.append({

                "指标": name,

                "最新值": value,

                "数据日期": date,

                "抓取时间": fetch_time

            })

            history_dict[name] = history

        else:

            st.warning(f"{name} 数据获取失败")

    except Exception as e:

        st.warning(f"{name} 获取失败: {e}")


# ======================
# 指标展示
# ======================

if indicator_data:

    metric_cols = st.columns(len(indicator_data))

    for idx, row in enumerate(indicator_data):

        hist = history_dict.get(row["指标"], [])

        if hist and len(hist) > 1:

            try:

                start_value = hist[0][1]
                end_value = hist[-1][1]

                change = (
                    (end_value - start_value)
                    / start_value
                ) * 100

                metric_cols[idx].metric(

                    label=row["指标"],

                    value=f"{row['最新值']:.2f}",

                    delta=f"{change:.2f}%"

                )

            except:

                metric_cols[idx].metric(

                    label=row["指标"],

                    value=f"{row['最新值']:.2f}"

                )

        else:

            metric_cols[idx].metric(

                label=row["指标"],

                value=f"{row['最新值']:.2f}"

            )

        metric_cols[idx].caption(

            f"数据日期：{row['数据日期']}\n"
            f"抓取时间：{row['抓取时间']}"

        )

else:

    st.info("暂无市场指标数据")


# ======================
# 单指标趋势图（Normalized）
# ======================

st.subheader("📈 单指标趋势图（Normalized）")

st.caption(
    "所有资产以起始点 = 100 进行归一化，方便比较真实走势"
)

for name, hist in history_dict.items():

    if hist:

        try:

            df = pd.DataFrame(

                hist,

                columns=["Date", "Value"]

            )

            df["Date"] = pd.to_datetime(df["Date"])

            # ======================
            # 数据清洗
            # ======================

            df["Value"] = pd.to_numeric(

                df["Value"],

                errors="coerce"

            )

            df = df.dropna()

            if len(df) < 2:

                continue

            # ======================
            # Normalized 处理
            # ======================

            base_value = df["Value"].iloc[0]

            if base_value == 0:

                continue

            df["Normalized"] = (

                df["Value"] / base_value

            ) * 100

            # ======================
            # Plotly 图表
            # ======================

            fig = go.Figure()

            fig.add_trace(

                go.Scatter(

                    x=df["Date"],

                    y=df["Normalized"],

                    mode="lines",

                    name=name

                )

            )

            fig.update_layout(

                title=f"{name}（Normalized）",

                xaxis_title="日期",

                yaxis_title="Normalized Index",

                hovermode="x unified",

                height=400,

                yaxis=dict(

                    autorange=True,

                    fixedrange=False

                )

            )

            st.plotly_chart(

                fig,

                use_container_width=True

            )

        except Exception as e:

            st.warning(f"{name} 图表生成失败: {e}")