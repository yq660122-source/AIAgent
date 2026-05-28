import requests

url = "http://www.xinhuanet.com/finance/"  # 示例页面
headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(url, headers=headers)
print(res.status_code)
print(res.text[:500])  # 打印前500字符