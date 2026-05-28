import feedparser

print("开始抓取...")

url = "https://www.federalreserve.gov/feeds/press_monetary.xml"

feed = feedparser.parse(url)

print("抓取完成")
print("新闻数量:", len(feed.entries))

for entry in feed.entries:
    print("=" * 50)
    print(entry.title)