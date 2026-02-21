import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
import time
from datetime import datetime

BASE_URL = "https://www.ptt.cc"
LIST_URL = "https://www.ptt.cc/bbs/home-sale/search?q=author%3Aceca"
DOWNLOADED_FILE = "downloaded_urls.txt"

def get_md5(text):
    return hashlib.md5(text.encode()).hexdigest()

def load_downloaded():
    if os.path.exists(DOWNLOADED_FILE):
        with open(DOWNLOADED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_downloaded(urls):
    with open(DOWNLOADED_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(urls)))

def fetch_list():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    time.sleep(3)
    
    for attempt in range(3):
        try:
            print(f"抓取文章清單... (第 {attempt+1} 次)")
            res = requests.get(LIST_URL, headers=headers, cookies={"over18": "1"}, timeout=30)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            
            articles = []
            for entry in soup.select("div.r-ent"):
                link_tag = entry.select_one(".title a")
                if not link_tag:
                    continue
                href = link_tag["href"]
                url = BASE_URL + href
                title = link_tag.text.strip()
                date = entry.select_one(".date").text.strip()
                articles.append({"title": title, "date": date, "url": url})
            return articles
            
        except Exception as e:
            print(f"第 {attempt+1} 次失敗：{e}")
            time.sleep(5)
    
    print("連續 3 次失敗，跳過")
    return []

def fetch_article_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    time.sleep(2)
    
    try:
        res = requests.get(url, headers=headers, cookies={"over18": "1"}, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        main = soup.select_one("#main-content")
        if not main:
            return ""
        
        for tag in main.select("span.f2, .push, .article-metaline"):
            tag.decompose()
        
        lines = [line.strip() for line in main.text.split("\n") if line.strip()]
        return "\n".join(lines)
    except:
        return ""

def crawl():
    print("🚀 開始檢查 PTT home-sale cec a 作者文章...")
    
    downloaded = load_downloaded()
    new_articles = []
    
    articles = fetch_list()
    print(f"📋 找到 {len(articles)} 篇文章")
    
    for art in articles:
        if art["url"] not in downloaded:
            new_articles.append(art)
    
    print(f"🆕 發現 {len(new_articles)} 篇新文章")
    
    if not new_articles:
        print("✅ 沒有新文章，結束")
        return
    
    os.makedirs("articles", exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    saved = 0
    
    for art in new_articles:
        try:
            content = fetch_article_content(art["url"])
            if not content:
                print(f"⏭️ 跳過空內容：{art['title'][:50]}")
                continue
            
            safe_title = get_md5(art["title"])
            filename = f"articles/{today}_{safe_title}.md"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {art['title']}\n\n")
                f.write(f"**來源：** {art['url']}\n")
                f.write(f"**日期：** {art['date']}\n\n")
                f.write("---\n\n")
                f.write(content)
            
            downloaded.add(art["url"])
            saved += 1
            print(f"💾 已存檔：{art['title'][:50]}...")
            
        except Exception as e:
            print(f"❌ 抓取失敗：{art['title'][:30]} - {e}")
    
    save_downloaded(downloaded)
    print(f"\n🎉 今天共存檔 {saved} 篇新文章")
    print(f"📁 所有文章在 articles/ 資料夾")

if __name__ == "__main__":
    crawl()
