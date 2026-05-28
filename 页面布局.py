# ======================
# 页面布局
# ======================
col1, col2 = st.columns([3, 1])

# ======================
# 左侧新闻区
# ======================
with col1:

    st.subheader("📰 GLOBAL FINANCIAL NEWS")

    # ======================
    # 新闻分区
    # ======================
    grouped_news = {}

    for item in news:
        source = item.get("country", "Unknown")
        if source not in grouped_news:
            grouped_news[source] = []
        grouped_news[source].append(item)

    # ======================
    # 分区显示
    # ======================
    for source, items in grouped_news.items():

        st.markdown(f"## 🌍 {source}")

        news_container = st.container(height=500)
        with news_container:

            for idx, row in enumerate(items):

                # ======================
                # 标题翻译
                # ======================
                title_data = translate_title(row["title"])

                # ======================
                # 风险标签
                # ======================
                tag_data = tag_news(row["title"])

                # ======================
                # 风险评分
                # ======================
                risk_score = calculate_risk_score(row["title"], tag_data.get("tags", []))
                risk_level = get_risk_level(risk_score)

                # 趋势判断
                if risk_score >= 80:
                    trend = "RISK OFF"
                elif risk_score >= 50:
                    trend = "VOLATILE"
                else:
                    trend = "NEUTRAL"

                # ======================
                # 新闻条目显示
                # ======================
                st.markdown(
                    f"""
<div style="
padding:8px;
border:1px solid #333;
border-radius:6px;
margin-bottom:8px;
">
<div style="
color:{tag_data.get('color', '#000')};
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
🕒 {row['date'].strftime('%Y-%m-%d %H:%M')}
| 🌍 {source}
| <a href=" 'link']}" target="_blank">原文</a >
</div>
</div>
                    """,
                    unsafe_allow_html=True
                )

                # ======================
                # AI分析折叠
                # ======================
                with st.expander(f"🤖 AI深度分析 #{source}-{idx+1}"):
                    analysis = fake_ai_analysis(row["title"])
                    st.info(analysis["summary"])
                    st.metric("风险评分", analysis["risk_score"])
                    st.write(f"风险等级：{analysis['risk_level']}")
                    st.write(f"市场趋势：{analysis['trend']}")

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


#-------------------------------------------------------------------------------------------------------------
# ======================
# 页面布局
# ======================
col1, col2 = st.columns([3, 1])

# ======================
# 左侧新闻区
# ======================
with col1:

    st.subheader("📰 GLOBAL FINANCIAL NEWS")

    # ======================
    # 新闻分区
    # ======================
    grouped_news = {}

    for item in news:
        source = item.get("country", "Unknown")
        if source not in grouped_news:
            grouped_news[source] = []
        grouped_news[source].append(item)

    # ======================
    # 分区显示
    # ======================
    for source, items in grouped_news.items():

        st.markdown(f"## 🌍 {source}")

        news_container = st.container(height=500)
        with news_container:

            for idx, row in enumerate(items):

                # ======================
                # 标题翻译
                # ======================
                title_data = translate_title(row["title"])

                # ======================
                # 风险标签
                # ======================
                tag_data = tag_news(row["title"])

                # ======================
                # 风险评分
                # ======================
                risk_score = calculate_risk_score(row["title"], tag_data.get("tags", []))
                risk_level = get_risk_level(risk_score)

                # 趋势判断
                if risk_score >= 80:
                    trend = "RISK OFF"
                elif risk_score >= 50:
                    trend = "VOLATILE"
                else:
                    trend = "NEUTRAL"

                # ======================
                # 新闻条目显示
                # ======================
                st.markdown(
                    f"""
<div style="
padding:8px;
border:1px solid #333;
border-radius:6px;
margin-bottom:8px;
">
<div style="
color:{tag_data.get('color', '#000')};
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
🕒 {row['date'].strftime('%Y-%m-%d %H:%M')}
| 🌍 {source}
| <a href="{row['link']}" target="_blank">原文</a>
</div>
</div>
                    """,
                    unsafe_allow_html=True
                )

                # ======================
                # AI分析折叠
                # ======================
                with st.expander(f"🤖 AI深度分析 #{source}-{idx+1}"):
                    analysis = fake_ai_analysis(row["title"])
                    st.info(analysis["summary"])
                    st.metric("风险评分", analysis["risk_score"])
                    st.write(f"风险等级：{analysis['risk_level']}")
                    st.write(f"市场趋势：{analysis['trend']}")
