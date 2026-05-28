def tag_news(title):

    title_lower = title.lower()

    # ======================
    # 高风险
    # ======================

    high_risk_keywords = [

        "war",

        "inflation",

        "crisis",

        "recession",

        "collapse",

        "conflict",

        "emergency"
    ]

    # ======================
    # 利率
    # ======================

    rate_keywords = [

        "rate",

        "fed",

        "ecb",

        "boj",

        "interest"
    ]

    # ======================
    # 流动性
    # ======================

    liquidity_keywords = [

        "liquidity",

        "balance sheet",

        "reserves",

        "funding"
    ]

    # ======================
    # 检测
    # ======================

    for word in high_risk_keywords:

        if word in title_lower:

            return {

                "tag": "🔴 HIGH RISK",

                "color": "#FF4B4B"
            }

    for word in rate_keywords:

        if word in title_lower:

            return {

                "tag": "🟠 RATE",

                "color": "#FFA500"
            }

    for word in liquidity_keywords:

        if word in title_lower:

            return {

                "tag": "🟢 LIQUIDITY",

                "color": "#00C853"
            }

    return {

        "tag": "🔵 MACRO",

        "color": "#4DA6FF"
    }