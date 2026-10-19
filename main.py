import os
import time
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import telebot

# Credentials
BOT_TOKEN = "8851245686:AAGSgnLfi3ysjHv_NL-lPxtl5xfm0rE4xck"
CHANNEL_ID = "@under50_lootdeals"
EARNKARO_ID = "5726805"

bot = telebot.TeleBot(BOT_TOKEN)

# Render Port Binding
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and posting deals!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Active Deal Feeds
SOURCES = [
    "https://www.reddit.com/r/IndianBeautyDeals/new.json?limit=10",
    "https://www.reddit.com/r/dealsforindia/new.json?limit=10"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DealsBot/2.0"}
posted_ids = set()

def create_affiliate_link(original_url):
    encoded = urllib.parse.quote(original_url, safe="")
    return f"https://earnkaro.com?r={EARNKARO_ID}&url={encoded}"

def check_and_post():
    for url in SOURCES:
        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code != 200:
                continue

            data = res.json()
            posts = data.get("data", {}).get("children", [])

            for post in posts:
                p = post.get("data", {})
                post_id = p.get("id")
                title = p.get("title", "")
                link = p.get("url_overridden_by_dest") or p.get("url") or ""

                if not post_id or post_id in posted_ids:
                    continue

                posted_ids.add(post_id)

                # EarnKaro link banana
                if "http" in link and "reddit.com" not in link:
                    buy_link = create_affiliate_link(link)
                else:
                    buy_link = f"https://earnkaro.com?r={EARNKARO_ID}"

                msg = (
                    f"🔥 *LOOT DEAL ALERT* 🔥\n\n"
                    f"📦 *{title}*\n\n"
                    f"🛒 *Grab Deal Here:*\n{buy_link}\n\n"
                    f"⚡ *Limited time loot! Jaldi order karein.*"
                )

                bot.send_message(CHANNEL_ID, msg, parse_mode="Markdown")
                print(f"Post ho gaya: {title[:30]}")
                time.sleep(3)

        except Exception as e:
            print(f"Error checking {url}: {e}")

if __name__ == "__main__":
    # Web server start
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Bot chalu ho gaya...")
    try:
        bot.send_message(CHANNEL_ID, "⚡ Deal Bot Activated! Deals aana shuru ho rahi hain...")
    except Exception as e:
        print(f"Startup message error: {e}")

    # Infinite Loop
    while True:
        check_and_post()
        time.sleep(60)  # Har 1 minute me check karega
