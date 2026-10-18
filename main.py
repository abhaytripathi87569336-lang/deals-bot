import requests
import xml.etree.ElementTree as ET
import re
import time
from urllib.parse import quote

BOT_TOKEN = "8883109486:AAHn2ZJIcyFPkJZ8By0H0lIBZPR5I6XHmEI"
CHAT_ID = "@under50deals_india"

posted_deals = set()
BLOCKED_KEYWORDS = ["pass", "coupon", "voucher", "ticket", "subscription", "solved", "paper", "quiz", "membership"]

def create_direct_shopping_link(clean_name, store):
    encoded_query = quote(clean_name)
    if "flipkart" in store.lower():
        return f"https://www.flipkart.com/search?q={encoded_query}&p%5B%5D=facets.price_range.test%3D0-50"
    else:
        return f"https://www.amazon.in/s?k={encoded_query}&rh=p_36%3A0-5000"

def send_telegram_deal(title, price, direct_url, store):
    message = (
        f"🔥 *LOOT DEAL UNDER ₹50!*\n\n"
        f"🏪 *Store:* {store}\n"
        f"📦 *Product:* {title}\n"
        f"💰 *Deal Price:* ₹{price}\n\n"
        f"🛒 [Seedha Product Kharidein Yahan Se]({direct_url})"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=12)
    except Exception as e:
        print(f"Send error: {e}")

def fetch_and_filter_deals():
    query = quote('("under 50" OR "rs 49" OR "rs 29" OR "rs 19") (site:amazon.in OR site:flipkart.com) -coupon -pass when:3h')
    feed_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        res = requests.get(feed_url, timeout=15)
        if res.status_code != 200:
            return
            
        root = ET.fromstring(res.content)
        items = root.findall(".//item")
        
        for item in items:
            title = item.find("title").text if item.find("title") is not None else ""
            clean_title = title.lower()
            
            if any(bad_word in clean_title for bad_word in BLOCKED_KEYWORDS):
                continue
            
            store = "Amazon" if "amazon" in clean_title else ("Flipkart" if "flipkart" in clean_title else None)
            if not store:
                continue

            price_match = re.search(r'(?:₹|Rs\.?|INR)\s?(\d+)', title, re.IGNORECASE)
            if price_match:
                price = int(price_match.group(1))
                if 0 < price <= 50 and title not in posted_deals:
                    short_name = re.sub(r' - (Flipkart|Amazon.*)', '', title).strip()
                    short_name = re.sub(r'(?:₹|Rs\.?|INR)\s?\d+', '', short_name).strip()
                    
                    direct_url = create_direct_shopping_link(short_name, store)
                    send_telegram_deal(short_name, price, direct_url, store)
                    posted_deals.add(title)
                    time.sleep(3)
    except Exception as e:
        print(f"Error: {e}")

while True:
    fetch_and_filter_deals()
    time.sleep(240)
