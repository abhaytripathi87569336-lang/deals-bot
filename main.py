import os
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configuration
BOT_TOKEN = "8883109486:AAHn2ZJIcyFPkJZ8By0H0lIBZPR5I6XHmEI"
CHANNEL_ID = "@under50deals_india"
EARNKARO_USER_ID = "5726805"
RENDER_APP_URL = "https://deals-bot-ycme.onrender.com"

# Verified active deal sources
FEEDS = [
    {
        "tag": "⚡ [LOOT DEAL ALERT]",
        "url": "https://www.desidime.com/feed",
        "btn_title": "🛒 Buy Now / View Deal",
        "btn_store": "🛍️ Flipkart Store",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=flipkart"
    },
    {
        "tag": "🔥 [PRICE DROP OFFER]",
        "url": "https://news.google.com/rss/search?q=" + quote("amazon loot deal offer price drop") + "&hl=en-IN&gl=IN&ceid=IN:en",
        "btn_title": "📦 Grab Amazon Deal",
        "btn_store": "🏷️ Amazon Deals Store",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=amazon"
    }
]

BLOCKED_WORDS = ["rummy", "fantasy", "casino", "win real cash", "earning app", "pass", "membership"]
posted_urls = set()

def send_telegram_deal(title, item_url, feed):
    monetized_link = f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=deal"
    
    clean_title = title.split(" - ")[0].strip()
    
    text = (
        f"{feed['tag']}\n\n"
        f"🏷️ Offer: {clean_title}\n\n"
        f"✅ Verified Low Price Deal!\n"
        f"🔗 Direct Source: {item_url}\n\n"
        f"👇 Niche diye gaye link se buy karein aur extra cashback payein:"
    )
    
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": feed["btn_title"], "url": monetized_link}],
                [{"text": feed["btn_store"], "url": feed["store_url"]}]
            ]
        }
    }
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, json=payload, timeout=15)
        return res.status_code == 200
    except Exception as e:
        print("Telegram Send Error:", e)
        return False

def check_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    # Startup verification message
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": "🚀 Deals Tracker Live! Scanners active."},
            timeout=10
        )
    except Exception:
        pass

    while True:
        for feed in FEEDS:
            try:
                resp = requests.get(feed["url"], headers=headers, timeout=15)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    items = root.findall("./channel/item")
                    
                    for item in items[:4]:
                        title = item.find("title").text if item.find("title") is not None else ""
                        link = item.find("link").text if item.find("link") is not None else ""
                        
                        if not link or link in posted_urls:
                            continue
                            
                        title_lower = title.lower()
                        if any(b in title_lower for b in BLOCKED_WORDS):
                            continue
                            
                        if send_telegram_deal(title, link, feed):
                            posted_urls.add(link)
                            print(f"[SUCCESS] Posted: {title}")
                            time.sleep(12)
            except Exception as e:
                print(f"[FEED ERROR] {feed['tag']}:", e)
            
            time.sleep(10)
        
        # Prevent memory leaks
        if len(posted_urls) > 300:
            posted_urls.clear()
            
        time.sleep(45)

# Self-pinger to keep Render from sleeping
def keep_alive_ping():
    while True:
        time.sleep(300)  # every 5 minutes
        try:
            requests.get(RENDER_APP_URL, timeout=10)
            print("[KEEP-ALIVE] Ping sent successfully")
        except Exception:
            pass

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online and working")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    t_bot = threading.Thread(target=check_deals, daemon=True)
    t_bot.start()
    
    t_ping = threading.Thread(target=keep_alive_ping, daemon=True)
    t_ping.start()
    
    run_server()
