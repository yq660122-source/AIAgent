from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime


@dataclass
class IntelligenceObject:

    # 基础信息
    title: str
    content: str
    source: str

    # 类型
    category: str = "MACRO"
    region: str = "GLOBAL"

    # 时间
    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )

    # 风险
    risk_level: str = "LOW"
    risk_score: int = 0

    # 标签
    tags: List[str] = field(default_factory=list)

    # AI分析
    ai_analysis: str = ""

    # 市场影响
    market_impact: Dict = field(default_factory=dict)

    # 原始链接
    url: str = ""

    # 情绪
    sentiment: str = "NEUTRAL"

    # 事件类型
    event_type: str = "GENERAL"

    def to_dict(self):

        return {
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "category": self.category,
            "region": self.region,
            "timestamp": self.timestamp,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "tags": self.tags,
            "ai_analysis": self.ai_analysis,
            "market_impact": self.market_impact,
            "url": self.url,
            "sentiment": self.sentiment,
            "event_type": self.event_type,
        }