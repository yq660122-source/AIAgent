from engines.risk_engine import calculate_risk_score
from engines.global_risk import calculate_risk_structure, calculate_global_risk
from engines.news_tagging import tag_news

def compute_risk_ball(news, market_stress=0, rate_stress=0):
    """
    计算 Risk Ball 的核心函数
    输入：
        news: list of dict，每条新闻必须包含"title"
        market_stress: float，市场压力值（可选）
        rate_stress: float，利率压力值（可选）
    输出：
        dict {
            "score": 全局风险分（0-100 float）
            "structure": 分类风险 dict {"INFLATION": int, "RATE": int,...}
        }
    """
    # -------------------------
    # 1. 单条新闻评分
    # -------------------------
    news_scores = []

    for item in news:
        # 使用 news_tagging 生成 tags
        tag_data = tag_news(item["title"])

        # 使用 calculate_risk_score 计算每条新闻分数
        score = calculate_risk_score(
            item["title"],
            tag_data.get("tags", [])
        )

        news_scores.append(score)

    # 调试输出（可选）
    print("NEWS SCORES:", news_scores)
    print("AVG SCORE:", sum(news_scores)/len(news_scores) if news_scores else 0)

    # -------------------------
    # 2. 全局风险分数（0-100）
    # -------------------------
    global_score = calculate_global_risk(
        news_scores,
        market_stress,
        rate_stress
    )

    # -------------------------
    # 3. 风险结构分类统计
    # -------------------------
    structure = calculate_risk_structure(news)

    # -------------------------
    # 4. 返回结果
    # -------------------------
    return {
        "score": global_score,
        "structure": structure
    }