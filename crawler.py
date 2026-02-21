import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def crawl():
    url = "https://www.ptt.cc/bbs/Stock/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, cookies={"over18": "1"})
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    for entry in soup.select("div.r-ent"):
        try:
            title  = entry.select_one(".title a").text.strip()
            author = entry.select_one(".author").text.strip()
            date   = entry.select_one(".date").text.strip()
            push   = entry.select_one(".nrec").text.strip()
            data.append({"push": push, "title": title, "author": author, "date": date})
        except AttributeError:
            pass

    df = pd.DataFrame(data)
    df.to_csv("output.csv", index=False, encoding="utf-8-sig")
    print(f"完成！共 {len(df)} 筆資料")

if __name__ == "__main__":
    crawl()
