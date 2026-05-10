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