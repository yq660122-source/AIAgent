# 文件名：app.py
import os
import streamlit as st
import requests
from openai import OpenAI  # DeepSeek SDK 兼容 OpenAI API

# -----------------------------
# 配置 DeepSeek API
# -----------------------------
DEEPSEEK_API_KEY = "sk-175cd729d88249309c7f64c06e886ab1"  # <-- 替换成你自己的
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# -----------------------------
# Streamlit 页面设置
# -----------------------------
st.set_page_config(page_title="AI Financial Intelligence System", layout="wide")
st.title("AI FINANCIAL INTELLIGENCE SYSTEM")

# -----------------------------
# 新闻抓取示例（美联储新闻）
# -----------------------------
st.header("US Fed 最新新闻")
try:
    url = "https://www.federalreserve.gov/newsevents/pressreleases.htm"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    news_html = resp.text

    # 这里可以自己解析 HTML 或直接用示例文本
    news_sample_text = "Fed announces interest rate change, inflation remains a concern."  # 占位文本
    st.write(news_sample_text)

except requests.exceptions.RequestException as e:
    st.error(f"新闻抓取失败: {e}")
    news_sample_text = ""

# -----------------------------
# DeepSeek 分析
# -----------------------------
st.header("新闻分析（DeepSeek）")

if news_sample_text:
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": "You are a financial news analyst"},
                {"role": "user", "content": news_sample_text}
            ],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
        )
        analysis_result = response.choices[0].message.content
        st.subheader("摘要 / 分析结果")
        st.write(analysis_result)

        # 示例：解析结果中的风险评分和趋势
        # 这里假设 DeepSeek 返回 JSON 格式 {"summary": "...", "risk_score": 0-10, "trend": "..."}
        # 如果返回纯文本，需要自己解析
        import json
        try:
            data = json.loads(analysis_result)
            st.metric("风险评分", data.get("risk_score", 0))
            st.metric("趋势", data.get("trend", "中性"))
        except json.JSONDecodeError:
            st.warning("无法解析 DeepSeek 返回结果为 JSON，只显示文本摘要")

    except Exception as e:
        st.error(f"新闻分析失败: {e}")

# -----------------------------
# 市场指标示例
# -----------------------------
st.header("市场指标")
# 占位指标示例
st.metric("S&P 500", "4,200", delta="+0.5%")
st.metric("NASDAQ", "13,500", delta="-0.3%")
st.metric("DXY 美元指数", "103.5", delta="+0.2%")

# -----------------------------
# 趋势图示例
# -----------------------------
st.header("趋势图")
import pandas as pd
import altair as alt

# 示例数据
df = pd.DataFrame({
    "日期": pd.date_range("2026-05-01", periods=5),
    "S&P 500": [4180, 4190, 4205, 4210, 4200],
    "NASDAQ": [13400, 13420, 13450, 13480, 13500]
})
df_melt = df.melt("日期", var_name="指数", value_name="数值")

chart = alt.Chart(df_melt).mark_line(point=True).encode(
    x="日期:T",
    y="数值:Q",
    color="指数:N"
).properties(width=700, height=400)

st.altair_chart(chart)