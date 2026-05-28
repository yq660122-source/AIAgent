RISK_SCORES = {

    "HIGH_RISK": 90,

    "RATE": 60,

    "LIQUIDITY": 70,

    "GEOPOLITICS": 85,

    "MARKET_STRESS": 75,
}


KEYWORD_WEIGHTS = {

    "emergency": 20,

    "crisis": 25,

    "collapse": 30,

    "war": 35,

    "recession": 20,

    "inflation": 15,

    "rate hike": 20,

    "default": 30,

    "bankruptcy": 25,

    "panic": 25,

    "attack": 30,
}


def calculate_risk_score(text, tags):

    text = text.lower()

    score = 0

    # 标签基础分
    for tag in tags:

        score += RISK_SCORES.get(tag, 0)

    # 关键词附加分
    for keyword, weight in KEYWORD_WEIGHTS.items():

        if keyword in text:

            score += weight

    # 限制最大值
    score = min(score, 100)

    return score


def get_risk_level(score):

    if score >= 80:
        return "EXTREME"

    elif score >= 60:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    else:
        return "LOW"