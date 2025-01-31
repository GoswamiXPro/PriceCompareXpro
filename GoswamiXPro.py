import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup
import time

# 🔹 Telegram BOT_TOKEN
BOT_TOKEN = "7690574371:AAHP0U6IkrZlu-fSPQW3d2nmUw5MgtIebAo"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔹 Websites for Price Comparison
WEBSITES = {
    "Amazon": "https://www.amazon.in/dp/{}",
    "Flipkart": "https://www.flipkart.com/search?q={}",
    "Meesho": "https://www.meesho.com/{}",
}

# 🔹 Store User Wishlist
user_wishlist = {}
price_alerts = {}

# 🔹 Function to send the main menu
def send_main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Price Comparison", callback_data="price_comparison"),
        InlineKeyboardButton("Price Alerts", callback_data="price_alerts"),
        InlineKeyboardButton("Wishlist", callback_data="wishlist"),
        InlineKeyboardButton("Product Recommendations", callback_data="recommendations"),
        InlineKeyboardButton("Trending Products", callback_data="trending_products"),
        InlineKeyboardButton("Currency Conversion", callback_data="currency_conversion"),
        InlineKeyboardButton("Help", callback_data="help")
    )
    bot.send_message(user_id, "Choose an option from the menu:", reply_markup=markup)

# 🔹 Price Comparison Menu
def send_price_comparison_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Compare One Product", callback_data="single_product_comparison"),
        InlineKeyboardButton("Compare Multiple Products", callback_data="multiple_product_comparison"),
        InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
    )
    bot.send_message(user_id, "🔹 Choose a comparison option:", reply_markup=markup)

# 🔹 Price Alerts Menu
def send_price_alerts_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Set Price Alert", callback_data="set_price_alert"),
        InlineKeyboardButton("View Price Alerts", callback_data="view_price_alerts"),
        InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
    )
    bot.send_message(user_id, "🔹 Choose an alert option:", reply_markup=markup)

# 🔹 Wishlist Menu
def send_wishlist_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("View Wishlist", callback_data="view_wishlist"),
        InlineKeyboardButton("Add to Wishlist", callback_data="add_to_wishlist"),
        InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
    )
    bot.send_message(user_id, "🔹 Choose a wishlist option:", reply_markup=markup)

# 🔹 Recommendations Menu
def send_recommendations_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Personalized Recommendations", callback_data="personalized_recommendations"),
        InlineKeyboardButton("Trending Recommendations", callback_data="trending_recommendations"),
        InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
    )
    bot.send_message(user_id, "🔹 Choose a recommendation option:", reply_markup=markup)

# 🔹 Handle Inline Keyboard Callback
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    if call.data == "price_comparison":
        send_price_comparison_menu(user_id)
    elif call.data == "price_alerts":
        send_price_alerts_menu(user_id)
    elif call.data == "wishlist":
        send_wishlist_menu(user_id)
    elif call.data == "recommendations":
        send_recommendations_menu(user_id)
    elif call.data == "trending_products":
        bot.send_message(user_id, "🔹 Fetching trending products...")
    elif call.data == "currency_conversion":
        bot.send_message(user_id, "🔹 Converting currency...")
    elif call.data == "help":
        bot.send_message(user_id, "🔹 Use this bot to compare prices, set price alerts, view wishlist, get recommendations, and more.")
    elif call.data == "main_menu":
        send_main_menu(user_id)
    elif call.data == "single_product_comparison":
        bot.send_message(user_id, "🔹 Send a product link to compare prices.")
    elif call.data == "multiple_product_comparison":
        bot.send_message(user_id, "🔹 Send multiple product links to compare prices.")
    elif call.data == "set_price_alert":
        bot.send_message(user_id, "🔹 Send a product link and your desired price to set a price alert.")
    elif call.data == "view_price_alerts":
        bot.send_message(user_id, "🔹 Viewing your price alerts...")
    elif call.data == "add_to_wishlist":
        bot.send_message(user_id, "🔹 Send a product link to add to your wishlist.")
    elif call.data == "view_wishlist":
        view_wishlist(user_id)
    bot.answer_callback_query(call.id)

# 🔹 Start Command with Main Menu
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    send_main_menu(user_id)

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

    table = "\n".join([f"{site}: {price}" for site, price in data])
    result = f"🛒 **Price Comparison** 🛒\n\n{table}\n🔹 Data Updated in Real-Time ✅"
    bot.send_message(user_id, result)

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

# 🔹 Fetch Price from Website
def fetch_price(website, product_id):
    try:
        url = WEBSITES[website].format(product_id)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        price = ""
        
        if website == "Amazon":
            price = soup.find("span", {"class": "a-price-whole"})
        elif website == "Flipkart":
            price = soup.find("div", {"class": "_30jeq3"})
        elif website == "Meesho":
            price = soup.find("h5", {"class": "pdp-price"})

        return price.text.strip() if price else "N/A"
    except:
        return "Error"

# 🔹 Wishlist Management
def view_wishlist(user_id):
    wishlist = user_wishlist.get(user_id, [])
    if wishlist:
        bot.send_message(user_id, f"Your wishlist: {', '.join(wishlist)}")
    else:
        bot.send_message(user_id, "❌ Your wishlist is empty.")

# 🔹 Price Alerts Functionality
def set_price_alert(user_id, product_id, target_price):
    price_alerts[user_id] = {'product_id': product_id, 'target_price': target_price}
    bot.send_message(user_id, f"✅ Price alert set for {product_id} at {target_price}!")

def check_price_alerts():
    for user_id, alert in price_alerts.items():
        current_price = fetch_price("Amazon", alert['product_id'])  # Modify based on site
        if float(current_price) <= alert['target_price']:
            bot.send_message(user_id, f"🔔 Price alert! The price of your product has dropped to {current_price}!")
            del price_alerts[user_id]  # Remove the alert after notifying

# 🔹 Run the bot
print("Bot is running...")
bot.polling(none_stop=True)