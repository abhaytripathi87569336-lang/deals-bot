import os
import time
import urllib.parse
import requests
import telebot

# Bot Token Render Environment Variables se aayega
BOT_TOKEN = "8851245686:AAGSgnLfi3ysjHv_NL-lPxtl5xfm0rE4xck"

# Aapke channel ka direct username aur EarnKaro referral ID
CHANNEL_ID = "@under50_lootdeals"
EARNKARO_ID = "5726805"

bot = telebot.TeleBot(BOT_TOKEN)

# Open India Deals feed (No Cloudflare blocking)
DEALS_URL = "https://www.reddit.com/r/IndianBeautyDeals/new.json?limit=10"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

posted_ids = set()

def make_earnkaro_link(target_url):
    encoded = urllib.parse.quote(target_url, safe="")
    return f"https://earnkaro.com?r={EARNKARO_ID}&url={encoded}"

def check_and_post_deals():
    try:
        response = requests.get(DEALS_URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Feed check status: {response.status_code}")
            return

        data = response.json()
        posts = data.get("data", {}).get("children", [])

        for post in posts:
            p_data = post.get("data", {})
            post_id = p_data.get("id")
            title = p_data.get("title", "")
            url = p_data.get("url_overridden_by_dest") or p_data.get("url")

            if not post_id or post_id in posted_ids:
                continue

            posted_ids.add(post_id)

            # Link convert karna EarnKaro format mein
            if "http" in str(url) and "reddit.com" not in str(url):
                aff_link = make_earnkaro_link(url)
            else:
                aff_link = f"https://earnkaro.com?r={EARNKARO_ID}"

            caption = (
                f"🔥 *SUPER LOOT DEAL* 🔥\n\n"
                f"📌 {title}\n\n"
                f"🛒 *Buy / Check Deal:*\n{aff_link}\n\n"
                f"⚡ Jaldi loots out of stock hone se pehle order karein!"
            )

            bot.send_message(CHANNEL_ID, caption, parse_mode="Markdown")
            print(f"Posted deal: {title[:30]}...")
            time.sleep(3)

    except Exception as e:
        print(f"Error checking deals: {e}")

if __name__ == "__main__":
    print("Bot starting up...")
    try:
        bot.send_message(CHANNEL_ID, "🚀 Daily Loot Deals Bot is LIVE & Ready!")
    except Exception as e:
        print(f"Telegram start msg failed: {e}")

    while True:
        check_and_post_deals()
        time.sleep(120)  # Har 2 minute me deals check karega
