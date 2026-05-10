import streamlit as st
import requests
import xml.etree.ElementTree as ET

st.title("AI Financial Intelligence System")

# 美联储 RSS 地址
url = "https://www.federalreserve.gov/feeds/press_monetary.xml"

try:
    r = requests.get(url)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    st.header("Federal Reserve News")
    # RSS里每条item
    items = root.findall('.//item')[:10]
    for item in items:
        title = item.find('title').text
        link = item.find('link').text
        st.write(title)
        st.write(link)
        st.write("---")
except Exception as e:
    st.error(f"抓取 RSS 出错: {e}")