import os
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Credentials
BOT_TOKEN = "8883109486:AAHn2ZJIcyFPkJZ8By0H0lIBZPR5I6XHmEI"
CHANNEL_ID = "@under50deals_india"
EARNKARO_USER_ID = "5726805"
RENDER_APP_URL = "https://deals-bot-ycme.onrender.com"

# Verified Indian deals feed
FEED_URL = "https://www.desidime.com/feed"

posted_urls = set()

def send_telegram_deal(title, item_url):
    clean_title = title.split(" - ")[0].strip()
    encoded_url = quote(item_url, safe="")
    monetized_link = f"https://earnkaro.com?r={EARNKARO_USER_ID}&url={encoded_url}"
    
    caption = (
        f"🔥 LOOT DEAL ALERT!\n\n"
        f"📦 {clean_title}\n\n"
        f"✅ Verified Deal\n\n"
        f"👇 Niche diye gaye link se buy karein aur cashback payein:"
    )
    
    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "disable_web_page_preview": False,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🛒 Buy Now / Grab Deal", "url": monetized_link}],
                [{"text": "🛍️ Flipkart Under ₹99", "url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=flipkart_deals"}]
            ]
        }
    }
    
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(api_url, json=payload, timeout=12)
        return res.status_code == 200
    except Exception as e:
        print("[Telegram Error]:", e)
        return False

def check_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    # Startup Alert
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": "🚀 Indian Deals Bot Online! Real loots active."},
            timeout=10
        )
    except Exception:
        pass

    while True:
        try:
            resp = requests.get(FEED_URL, headers=headers, timeout=15)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                items = root.findall("./channel/item")
                
                for item in items[:5]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    
                    if not link or link in posted_urls:
                        continue
                    
                    if send_telegram_deal(title, link):
                        posted_urls.add(link)
                        print(f"[POSTED]: {title}")
                        time.sleep(12)
        except Exception as e:
            print("[Fetch Error]:", e)
        
        # Memory cleanup
        if len(posted_urls) > 500:
            posted_urls.clear()
            
        time.sleep(60)

def keep_alive():
    while True:
        time.sleep(240)
        try:
            requests.get(RENDER_APP_URL, timeout=10)
        except Exception:
            pass

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=check_deals, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    run_server()
