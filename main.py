import os
import time
import requests
import feedparser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
EARNKARO_USER_ID = "5726805"

# Multi-Store & Multi-Category Feeds
CATEGORIES = [
    {
        "tag": "⚡ [LOOT DEALS UNDER ₹50]",
        "query": "loot deals under 50 amazon flipkart online sale",
        "btn_primary": "🛒 Open Loot Deal",
        "btn_store": "🛍️ Flipkart Under ₹99",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=flipkart_deals"
    },
    {
        "tag": "🎧 [TECH & ACCESSORIES UNDER ₹99]",
        "query": "electronics earphones cables under 99 amazon",
        "btn_primary": "🔥 Grab Tech Loot",
        "btn_store": "📦 Amazon Tech Deals",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=amazon_tech"
    },
    {
        "tag": "👕 [FASHION 80-90% OFF STEAL]",
        "query": "fashion loot 90 percent off amazon flipkart ajio",
        "btn_primary": "👗 View Fashion Deal",
        "btn_store": "🏷️ 90% Off Fashion Store",
        "store_url": f"https://earnkaro.com?r={EARNKARO_USER_ID}&fname=fashion_loot"
    }
]

# Blacklist unwanted keywords / promotions
BLOCKED_WORDS = [
    "titan", "pass", "membership", "subscribe", "coupon code",
    "voucher", "rummy", "fantasy", "casino", "win real cash", "earning app"
]

posted_urls = set()

def send_telegram_deal(title, item_url, cat):
    # Automated monetized redirect link via your EarnKaro ID
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

def check_deals():
    while True:
        try:
            for cat in CATEGORIES:
                rss_url = f"https://news.google.com/rss/search?q={cat['query'].replace(' ', '+')}+when:1h&hl=en-IN&gl=IN&ceid=IN:en"
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:2]:
                    title = entry.title
                    link = entry.link
                    
                    if link in posted_urls:
                        continue
                    
                    title_lower = title.lower()
                    if any(bad in title_lower for bad in BLOCKED_WORDS):
                        continue
                    
                    if send_telegram_deal(title, link, cat):
                        posted_urls.add(link)
                        print(f"Posted: {cat['tag']} - {title}")
                        time.sleep(15)
                
                time.sleep(20)
        except Exception as e:
            print("Scan Error:", e)
        
        # Check feeds every 3 minutes
        time.sleep(180)

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
