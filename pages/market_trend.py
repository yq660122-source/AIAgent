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

col1, col2, col3 = st.columns(3)

with col1:
    st.button("🏠 返回首页")

with col2:
    st.button("🌍 全球风险监控")

with col3:
    st.button("🤖 AI宏观分析")

# ======================
# 时间窗口
# ======================

window = st.selectbox(
    "时间窗口",
    ["7D", "30D", "90D", "ALL"],
    index=2
)

window_map = {
    "7D": 7,
    "30D": 30,
    "90D": 90,
    "ALL": None
}

days = window_map[window]

# ======================
# 数据源
# ======================

FRED_SERIES = {
    "S&P 500": "SP500",
    "US 10Y": "DGS10",
    "Gold": "GOLDAMGBD228NLBM",
    "Oil": "DCOILWTICO",
    "USD/CNY": "DEXCHUS"
}

history_dict = {}
indicator_data = []

for name, sid in FRED_SERIES.items():
    try:
        date, value, history, fetch_time = get_fred_latest(sid)

        if value is None:
            continue

        indicator_data.append({
            "name": name,
            "value": value,
            "date": date,
            "time": fetch_time
        })

        history_dict[name] = history

    except Exception as e:
        st.warning(f"{name} error: {e}")

# ======================
# 指标卡片
# ======================

if indicator_data:
    cols = st.columns(len(indicator_data))

    for i, item in enumerate(indicator_data):

        hist = history_dict[item["name"]]

        delta = None

        if hist and len(hist) > 2:
            try:
                start = float(hist[0][1])
                end = float(hist[-1][1])
                delta = f"{((end-start)/start)*100:.2f}%"
            except:
                pass

        cols[i].metric(
            item["name"],
            f"{item['value']:.2f}",
            delta
        )

        cols[i].caption(item["date"])

else:
    st.info("No data")

# ======================
# 🔥 核心修复：Overview（正确金融画法）
# ======================

st.subheader("🌐 Overview (True Market Comparison)")

fig = go.Figure()

for name, hist in history_dict.items():

    if not hist:
        continue

    df = pd.DataFrame(hist, columns=["Date", "Value"])

    df["Date"] = pd.to_datetime(df["Date"])
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df = df.dropna().sort_values("Date")

    # 时间窗口（只截数据，不做resample）
    if days:
        df = df.tail(days)

    if len(df) < 2:
        continue

    # ❗关键：只用真实观测点，不插值、不对齐
    base = df["Value"].iloc[0]

    if base == 0:
        continue

    df["Normalized"] = df["Value"] / base * 100

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Normalized"],
            mode="lines",
            name=name
        )
    )

fig.add_hline(y=100, line_dash="dash")

fig.update_layout(
    height=600,
    hovermode="x unified",
    title=f"Cross Asset Performance ({window})",
    xaxis_title="Date",
    yaxis_title="Normalized (Base=100)"
)

st.plotly_chart(fig, use_container_width=True)

# ======================
# Individual charts（原始值）
# ======================

st.subheader("📈 Individual Assets")

for name, hist in history_dict.items():

    if not hist:
        continue

    df = pd.DataFrame(hist, columns=["Date", "Value"])

    df["Date"] = pd.to_datetime(df["Date"])
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    df = df.dropna().sort_values("Date")

    if days:
        df = df.tail(days)

    if len(df) < 2:
        continue

    start = df["Value"].iloc[0]
    end = df["Value"].iloc[-1]

    change = ((end - start) / start) * 100

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Value"],
            mode="lines",
            name=name
        )
    )

    fig.update_layout(
        title=f"{name} | {change:.2f}%",
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)