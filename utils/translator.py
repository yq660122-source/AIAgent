def translate_title(title):

    title_lower = title.lower()

    translations = {

        "federal reserve": "美联储",

        "interest rate": "利率",

        "inflation": "通胀",

        "economic growth": "经济增长",

        "policy": "政策",

        "monetary": "货币",

        "bank": "银行",

        "financial": "金融",

        "market": "市场",

        "stability": "稳定",

        "press release": "新闻发布",

        "statement": "声明"
    }

    translated = title

    for eng, cn in translations.items():

        translated = translated.replace(
            eng,
            cn
        )

        translated = translated.replace(
            eng.title(),
            cn
        )

    return {

        "original": title,

        "translated": translated
    }