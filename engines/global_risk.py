def calculate_global_risk(news):

    risk_scores = {

        "通胀风险": 0,

        "利率风险": 0,

        "流动性风险": 0,

        "地缘政治风险": 0,

        "市场波动": 0
    }

    for item in news:

        title = item["title"].lower()

        # ======================
        # 通胀
        # ======================

        if "inflation" in title:

            risk_scores["通胀风险"] += 2

        # ======================
        # 利率
        # ======================

        if (

            "rate" in title

            or "fed" in title

            or "ecb" in title
        ):

            risk_scores["利率风险"] += 2

        # ======================
        # 流动性
        # ======================

        if (

            "liquidity" in title

            or "funding" in title
        ):

            risk_scores["流动性风险"] += 2

        # ======================
        # 地缘政治
        # ======================

        if (

            "war" in title

            or "conflict" in title

            or "military" in title
        ):

            risk_scores["地缘政治风险"] += 3

        # ======================
        # 波动
        # ======================

        if (

            "volatility" in title

            or "uncertainty" in title
        ):

            risk_scores["市场波动"] += 2

    return risk_scores