import telebot
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

# 🔹 Telegram Bot BOT_TOKEN
BOT_TOKEN = "7690574371:AAHP0U6IkrZlu-fSPQW3d2nmUw5MgtIebAo"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔹 Websites for Price Comparison
WEBSITES = {
    "Amazon": "https://www.amazon.in/dp/{}",
    "Flipkart": "https://www.flipkart.com/search?q={}",
    "Meesho": "https://www.meesho.com/{}",
}

# 🔹 Store User Wishlist & Tracking Data
user_watchlist = {}
price_tracking = {}

# 🔹 Function to fetch product details (Title, Image, Price, Rating)
def fetch_product_details(website, product_id):
    try:
        url = WEBSITES[website].format(product_id)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract product details
        title = soup.find("span", {"id": "productTitle"}).text.strip() if website == "Amazon" else "N/A"
        price = soup.find("span", {"class": "a-price-whole"}) if website == "Amazon" else None
        rating = soup.find("span", {"class": "a-icon-alt"}) if website == "Amazon" else None
        image = soup.find("img", {"id": "landingImage"})["src"] if website == "Amazon" else "N/A"

        return {
            "title": title,
            "price": price.text.strip() if price else "N/A",
            "rating": rating.text.strip() if rating else "N/A",
            "image": image
        }
    except:
        return {"title": "N/A", "price": "Error", "rating": "N/A", "image": "N/A"}

# 🔹 Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(user_id, "🔹 **Welcome to Goswami X Pro!** 🔹\n\n"
                              "Send a product link to compare prices.", parse_mode="Markdown")

# 🔹 Handle Product Link & Show Prices
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def handle_message(message):
    user_id = message.chat.id
    product_id = extract_product_id(message.text)
    
    if not product_id:
        bot.send_message(user_id, "❌ Invalid product link. Please send a correct product link.")
        return

    data = []
    for site in WEBSITES:
        details = fetch_product_details(site, product_id)
        data.append([site, details["price"], details["rating"]])

    table = tabulate(data, headers=["Website", "Price", "Rating"], tablefmt="grid")
    result = f"🛒 **Goswami X Pro Price Comparison** 🛒\n\n```\n{table}\n```\n🔹 Data Updated in Real-Time ✅"

    bot.send_message(user_id, result, parse_mode="Markdown")

# 🔹 Wishlist Feature
@bot.message_handler(commands=['wishlist'])
def wishlist(message):
    user_id = message.chat.id
    if user_id in user_watchlist and user_watchlist[user_id]:
        wishlist_items = "\n".join(user_watchlist[user_id])
        bot.send_message(user_id, f"📌 **Your Wishlist:**\n{wishlist_items}", parse_mode="Markdown")
    else:
        bot.send_message(user_id, "📝 Your wishlist is empty. Add products by sending `/addwishlist <Product Link>`.")

@bot.message_handler(commands=['addwishlist'])
def add_to_wishlist(message):
    user_id = message.chat.id
    product_id = extract_product_id(message.text.replace("/addwishlist ", ""))

    if product_id:
        if user_id not in user_watchlist:
            user_watchlist[user_id] = []
        user_watchlist[user_id].append(product_id)
        bot.send_message(user_id, "✅ Added to Wishlist!")
    else:
        bot.send_message(user_id, "❌ Invalid Product Link.")

# 🔹 Price Drop Alerts
def track_prices():
    while True:
        for user_id, product_id in price_tracking.items():
            for site in WEBSITES:
                details = fetch_product_details(site, product_id)
                current_price = details["price"]
                if current_price != "N/A" and float(current_price.replace(",", "")) < float(price_tracking[user_id]):
                    bot.send_message(user_id, f"🔥 **Price Drop Alert!**\n{site}: ₹{current_price}")
        time.sleep(3600)

@bot.message_handler(commands=['track'])
def track_product(message):
    user_id = message.chat.id
    product_id = extract_product_id(message.text.replace("/track ", ""))

    if product_id:
        price_tracking[user_id] = product_id
        bot.send_message(user_id, "🔔 Price tracking activated! You’ll get notified on price drops.")
    else:
        bot.send_message(user_id, "❌ Invalid product link.")

# 🔹 Extract Product ID from URL
def extract_product_id(url):
    try:
        if "amazon" in url:
            return url.split("/dp/")[1].split("/")[0]
        elif "flipkart" in url:
            return url.split("search?q=")[1].split("&")[0]
        elif "meesho" in url:
            return url.split(".com/")[1].split("/")[0]
        else:
            return None
    except:
        return None

# 🔹 Multi-language Support
@bot.message_handler(commands=['language'])
def change_language(message):
    user_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi"),
               InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
    bot.send_message(user_id, "🌍 Select your language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    lang = "Hindi" if call.data == "lang_hi" else "English"
    bot.send_message(call.message.chat.id, f"✅ Language set to {lang}!")

# 🔹 Run the bot
import threading
threading.Thread(target=track_prices, daemon=True).start()
print("Bot is running...")
bot.polling()