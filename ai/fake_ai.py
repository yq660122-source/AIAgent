from engines.risk_engine import (
    calculate_risk_score,
    get_risk_level
)


def fake_ai_analysis(news_title):

    title_lower = news_title.lower()

    # ======================
    # 风险引擎
    # ======================

    risk_score = calculate_risk_score(
        news_title,
        []
    )

    risk_level = get_risk_level(
        risk_score
    )

    # ======================
    # 趋势判断（兼容旧系统）
    # ======================

    if risk_score >= 80:

        trend = "RISK OFF"

    elif risk_score >= 50:

        trend = "VOLATILE"

    else:

        trend = "NEUTRAL"

    # ======================
    # AI分析内容
    # ======================

    summary = f"""
【中文翻译】
{news_title}

【市场解读】
该新闻可能对全球金融市场产生影响。
"""

    # ======================
    # 补充分析
    # ======================

    if "inflation" in title_lower:

        summary += """
通胀相关消息通常意味着：

- 美联储可能维持高利率
- 美股承压
- 黄金波动加剧
"""

    elif "rate" in title_lower:

        summary += """
利率相关消息可能影响：

- 美债收益率
- 美元指数
- 全球风险资产
"""

    elif "growth" in title_lower:

        summary += """
经济增长相关消息通常利好：

- 股票市场
- 风险偏好
"""

    # ======================
    # 返回结果
    # ======================

    return {

        "summary": summary,

        "risk_score": risk_score,

        "trend": trend,

        "risk_level": risk_level
    }