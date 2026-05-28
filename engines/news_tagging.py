RISK_RULES = {

    "HIGH_RISK": [
        "war",
        "conflict",
        "collapse",
        "crisis",
        "recession",
        "bankruptcy",
        "default",
        "emergency",
        "sanction",
        "attack",
    ],

    "RATE": [
        "inflation",
        "interest rate",
        "fed",
        "ecb",
        "tightening",
        "hike",
        "cpi",
        "hawkish",
    ],

    "LIQUIDITY": [
        "liquidity",
        "balance sheet",
        "credit",
        "debt",
        "funding",
        "bank reserves",
    ],

    "GEOPOLITICS": [
        "china",
        "russia",
        "ukraine",
        "nato",
        "taiwan",
        "middle east",
    ],

    "MARKET_STRESS": [
        "volatility",
        "selloff",
        "panic",
        "market crash",
        "bond yields",
    ]
}


RISK_COLORS = {

    "HIGH_RISK": {
        "color": "#ff4b4b",
        "label": "HIGH RISK",
        "icon": "🔴"
    },

    "RATE": {
        "color": "#ff9800",
        "label": "RATE",
        "icon": "🟠"
    },

    "LIQUIDITY": {
        "color": "#2196f3",
        "label": "LIQUIDITY",
        "icon": "🔵"
    },

    "GEOPOLITICS": {
        "color": "#9c27b0",
        "label": "GEOPOLITICS",
        "icon": "🟣"
    },

    "MARKET_STRESS": {
        "color": "#ffd600",
        "label": "MARKET STRESS",
        "icon": "🟡"
    },

    "NORMAL": {
        "color": "#00c853",
        "label": "NORMAL",
        "icon": "🟢"
    }
}


def tag_news(text):

    text = text.lower()

    tags = []

    for category, keywords in RISK_RULES.items():

        for keyword in keywords:

            if keyword in text:

                if category not in tags:

                    tags.append(category)

    # 兼容旧系统
    if not tags:

        return {
    "tags": [],

    # 兼容旧系统
    "tag": "NORMAL",

    "color": "#00c853",

    "label": "NORMAL",

    "icon": "🟢"
}

    primary = tags[0]

    risk_data = RISK_COLORS.get(primary)

    return {
    "tags": tags,

    # 兼容旧系统
    "tag": risk_data["label"],

    "color": risk_data["color"],

    "label": risk_data["label"],

    "icon": risk_data["icon"]
}


