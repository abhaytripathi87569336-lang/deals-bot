import os
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configuration
BOT_TOKEN = 8883109486:AAHn2ZJIcyFPkJZ8By0H0lIBZPR5I6XHmEI"
CHANNEL_ID = "@under50deals_india"
EARNKARO_USER_ID = "5726805"

# Multi-Store & Multi-Category Feeds
CATEGORIES = [
    {
        "tag": "⚡ [LOOT DEALS UNDER ₹50]",
        "query": "loot deals under 50 amazon flipkart",
        "btn_primary": "🛒 Open Loot Deal",
        "btn_store": "🛍️ Flipkart Under ₹99",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=flipkart_deals"
    },
    {
        "tag": "🎧 [TECH & ACCESSORIES UNDER ₹99]",
        "query": "tech accessories under 99 amazon",
        "btn_primary": "🔥 Grab Tech Loot",
        "btn_store": "📦 Amazon Tech Deals",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=amazon_tech"
    },
    {
        "tag": "👕 [FASHION 80-90% OFF STEAL]",
        "query": "fashion sale discount amazon flipkart",
        "btn_primary": "👗 View Fashion Deal",
        "btn_store": "🏷️ 90% Off Fashion Store",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=fashion_loot"
    }
]

BLOCKED_WORDS = [
    "titan", "pass", "membership", "subscribe", "coupon code",
    "voucher", "rummy", "fantasy", "casino", "win real cash", "earning app"
]

posted_urls = set()

def send_telegram_deal(title, item_url, cat):
    monetized_primary = f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=deal"
    
    caption = (
        f"{cat['tag']}\n\n"
        f"🔥 *{title}*\n\n"
        f"✅ *Verified Low Price Offer!*\n"
        f"⚡ Direct Link: [Click Here to View]({item_url})\n\n"
        f"👇 *Niche diye gaye buttons se buy karein aur extra cashback payein:*"
    )
    
    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": cat["btn_primary"], "url": monetized_primary}
                ],
                [
                    {"text": cat["btn_store"], "url": cat["store_url"]}
                ]
            ]
        }
    }
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print("Telegram Send Error:", e)
        return False

def send_test_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": "🤖 *Deals Bot Online!*\n\nAmazon & Flipkart multi-category deals tracker fully active with auto-cashback links.",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Startup ping failed:", e)

def check_deals():
    send_test_message()
    while True:
        try:
            for cat in CATEGORIES:
                encoded_query = quote(cat['query'])
                rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
                
                resp = requests.get(rss_url, timeout=10)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    items = root.findall("./channel/item")
                    
                    for item in items[:2]:
                        title = item.find("title").text if item.find("title") is not None else ""
                        link = item.find("link").text if item.find("link") is not None else ""
                        
                        if not link or link in posted_urls:
                            continue
                        
                        title_lower = title.lower()
                        if any(bad in title_lower for bad in BLOCKED_WORDS):
                            continue
                        
                        if send_telegram_deal(title, link, cat):
                            posted_urls.add(link)
                            print(f"Posted: {cat['tag']} - {title}")
                            time.sleep(10)
                
                time.sleep(15)
        except Exception as e:
            print("Scan Error:", e)
        
        time.sleep(90)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"All-in-One Multi-Store Deals Bot Active")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    t_bot = threading.Thread(target=check_deals, daemon=True)
    t_bot.start()
    run_server()
    
