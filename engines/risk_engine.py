from datetime import datetime, timedelta
import math

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

# =========================
# 🔥 单条新闻风险评分（升级版）
# =========================

def calculate_risk_score(text, tags, timestamp=None):

    text = text.lower()

    score = 0

    # -------------------------
    # 1. tag基础分（归一化）
    # -------------------------
    tag_score = 0
    for tag in tags:
        tag_score += RISK_SCORES.get(tag, 0)

    tag_score = min(tag_score, 100)

    # -------------------------
    # 2. keyword分
    # -------------------------
    keyword_score = 0
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword in text:
            keyword_score += weight

    keyword_score = min(keyword_score, 100)

    # -------------------------
    # 3. 时间衰减（关键升级）
    # -------------------------
    time_factor = 1.0

    if timestamp:
        try:
            if isinstance(timestamp, str):
                ts = datetime.fromisoformat(timestamp)
            else:
                ts = timestamp

            hours_old = (datetime.utcnow() - ts).total_seconds() / 3600

            # 24小时内最强，之后指数衰减
            time_factor = math.exp(-hours_old / 48)

        except:
            time_factor = 1.0

    # -------------------------
    # 4. 合成评分（核心）
    # -------------------------
    raw_score = tag_score * 0.6 + keyword_score * 0.4

    score = raw_score * (0.5 + 0.5 * time_factor)

    return min(round(score, 2), 100)


# =========================
# 🔥 风险等级
# =========================

def get_risk_level(score):

    if score >= 80:
        return "EXTREME"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


# =========================
# 🔥 聚合风险（新增：风险球核心）
# =========================

def calculate_global_risk(news_scores, market_stress=0, rate_stress=0):

    if not news_scores:
        return 0

    # 新闻平均风险
    news_risk = sum(news_scores) / len(news_scores)

    # 市场结构风险
    structural = (
        market_stress * 0.5 +
        rate_stress * 0.5
    )

    # 最终风险球
    final = (
        news_risk * 0.5 +
        structural * 0.5
    )

    return min(round(final, 2), 100)