import telebot
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔹 Telegram Bot BOT_TOKEN
BOT_TOKEN = "7690574371:AAHP0U6IkrZlu-fSPQW3d2nmUw5MgtIebAo"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔹 Websites for Price Comparison
WEBSITES = {
    "Amazon": "https://www.amazon.in/dp/{}",
    "Flipkart": "https://www.flipkart.com/search?q={}",
    "Meesho": "https://www.meesho.com/{}",
}

# 🔹 Store User Wishlist
user_watchlist = {}

# 🔹 Function to fetch product price
def fetch_price(website, product_id):
    try:
        url = WEBSITES[website].format(product_id)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract price based on website
        if website == "Amazon":
            price = soup.find("span", {"class": "a-price-whole"})
        elif website == "Flipkart":
            price = soup.find("div", {"class": "_30jeq3"})
        elif website == "Meesho":
            price = soup.find("h5", {"class": "pdp-price"})

        return price.text.strip() if price else "N/A"
    except:
        return "Error"

# 🔹 Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(user_id, 
                     "🔹 **Welcome to Goswami X Pro!** 🔹\n\n"
                     "Send a product link to compare prices.", 
                     parse_mode="Markdown")

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
        price = fetch_price(site, product_id)
        data.append([site, price])

    table = tabulate(data, headers=["Website", "Price"], tablefmt="grid")
    result = f"🛒 **Goswami X Pro Price Comparison** 🛒\n\n```\n{table}\n```\n🔹 Data Updated in Real-Time ✅"

    bot.send_message(user_id, result, parse_mode="Markdown")

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

# 🔹 Run the bot
print("Bot is running...")
bot.polling()