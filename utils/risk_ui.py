import streamlit as st


def get_risk_color(score):
    if score < 40:
        return "#2ecc71"  # green
    elif score < 60:
        return "#f1c40f"  # yellow
    elif score < 80:
        return "#e67e22"  # orange
    else:
        return "#e74c3c"  # red


def render_risk_ball(score):

    color = get_risk_color(score)

    html = f"""
    <style>
    .risk-container {{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-top:10px;
        margin-bottom:10px;
    }}

    .risk-ball {{
        width:120px;
        height:120px;
        border-radius:50%;
        background:{color};
        box-shadow:0 0 25px {color};
        animation:pulse 2s infinite;
        cursor:pointer;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
        color:white;
        font-weight:bold;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); opacity:0.8; }}
        50% {{ transform: scale(1.1); opacity:1; }}
        100% {{ transform: scale(1); opacity:0.8; }}
    }}
    </style>

    <div class="risk-container">
        <div class="risk-ball">
            <div>RISK</div>
            <div style="font-size:20px">{int(score)}</div>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)