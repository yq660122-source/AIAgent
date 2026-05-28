def calculate_market_state(

    spy_change,

    treasury_change,

    gold_change

):

    # ======================
    # Risk On
    # ======================

    if (

        spy_change > 0

        and treasury_change < 0

    ):

        return {

            "state": "🟢 RISK ON",

            "description":
            "股票市场风险偏好较强"
        }

    # ======================
    # Risk Off
    # ======================

    elif (

        spy_change < 0

        and gold_change > 0

    ):

        return {

            "state": "🔴 RISK OFF",

            "description":
            "避险情绪上升"
        }

    # ======================
    # High Volatility
    # ======================

    else:

        return {

            "state": "🟠 HIGH VOLATILITY",

            "description":
            "市场波动较大"
        }