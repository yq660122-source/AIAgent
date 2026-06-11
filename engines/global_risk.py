def calculate_risk_structure(news):

    risk_scores = {
        "INFLATION": 0,
        "RATE": 0,
        "LIQUIDITY": 0,
        "GEOPOLITICS": 0,
        "VOLATILITY": 0
    }

    for item in news:

        title = item["title"].lower()

        if "inflation" in title:
            risk_scores["INFLATION"] += 1

        if "rate" in title or "fed" in title or "ecb" in title:
            risk_scores["RATE"] += 1

        if "liquidity" in title or "funding" in title:
            risk_scores["LIQUIDITY"] += 1

        if "war" in title or "conflict" in title:
            risk_scores["GEOPOLITICS"] += 1

        if "volatility" in title or "uncertainty" in title:
            risk_scores["VOLATILITY"] += 1

    return risk_scores


# （保留你原来的函数，如果还在用）
def calculate_global_risk(news_scores, market_stress=0, rate_stress=0):

    if not news_scores:
        return 0

    news_risk = sum(news_scores) / len(news_scores)

    structural = (market_stress * 0.5 + rate_stress * 0.5)

    final = (news_risk * 0.5 + structural * 0.5)

    return min(round(final, 2), 100)