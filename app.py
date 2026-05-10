import subprocess
import sys

# 安装依赖
subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

import streamlit as st
import feedparser

st.title("AI Financial Intelligence System")

url = "https://www.federalreserve.gov/feeds/press_monetary.xml"

feed = feedparser.parse(url)

st.header("Federal Reserve News")

for entry in feed.entries[:10]:
    st.write(entry.title)
    st.write(entry.link)
    st.write("---")