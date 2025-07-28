import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")
CHANNEL_USERNAME = "@newcastle1"

# === БАЗА ДАННЫХ (ФАЙЛЫ) ===
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def get_user(user_id):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {"balance": 1000, "cars": []}
        save_users(users)
    return users[user_id]

def update_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

# === ПРОВЕРКА ПОДПИСКИ ===
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# === КОМАНДА /START ===
@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub"))
        bot.send_message(message.chat.id, "❗ Подпишись на канал для доступа к боту.", reply_markup=markup)
        return

    # Главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚗 Автосалон", "🚘 Гараж")
    markup.row("💼 Профиль")

    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"👤 {message.from_user.first_name}\n💼 Баланс: {user['balance']}₽",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub(c):
    if is_subscribed(c.from_user.id):
        bot.delete_message(c.message.chat.id, c.message.message_id)
        start(c.message)
    else:
        bot.answer_callback_query(c.id, "❌ Подпишись сначала!")

# === СЛОВАРЬ МАШИН ===
cars = {
    "BMW": [
        {"model": "BMW M5", "price": 500},
        {"model": "BMW X6", "price": 700}
    ],
    "Mercedes": [
        {"model": "Mercedes E63", "price": 800},
        {"model": "Mercedes GLE", "price": 1000}
    ]
}

# === МЕНЮ ===
@bot.message_handler(func=lambda msg: msg.text in ["🚗 Автосалон", "🚘 Гараж", "💼 Профиль"])
def menu(msg):
    user = get_user(msg.from_user.id)

    if msg.text == "🚗 Автосалон":
        markup = types.InlineKeyboardMarkup()
        for brand in cars:
            markup.add(types.InlineKeyboardButton(brand, callback_data=f"brand_{brand}"))
        bot.send_message(msg.chat.id, "Выбери марку:", reply_markup=markup)

    elif msg.text == "🚘 Гараж":
        if not user["cars"]:
            bot.send_message(msg.chat.id, "🚘 У тебя нет машин.")
        else:
            text = "🚘 Твой гараж:\n" + "\n".join(user["cars"])
            bot.send_message(msg.chat.id, text)

    elif msg.text == "💼 Профиль":
        bot.send_message(msg.chat.id, f"👤 {msg.from_user.first_name}\n💰 Баланс: {user['balance']}₽")

# === ВЫБОР МАРКИ ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("brand_"))
def show_models(c):
    brand = c.data.split("_")[1]
    markup = types.InlineKeyboardMarkup()
    for car in cars[brand]:
        cb_data = f"buy_{brand}_{car['model'].replace(' ', '_')}"
        markup.add(types.InlineKeyboardButton(f"{car['model']} - {car['price']}₽", callback_data=cb_data))
    bot.edit_message_text(
        f"🚗 {brand} — выбери модель:",
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        reply_markup=markup
    ) 
# === ПОКУПКА ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy_car(c):
    parts = c.data.split("_")
    brand = parts[1]
    model = " ".join(parts[2:])
    car_data = next((car for car in cars[brand] if car["model"] == model), None)

    if not car_data:
        bot.answer_callback_query(c.id, "Машина не найдена.")
        return

    user = get_user(c.from_user.id)

    if user["balance"] < car_data["price"]:
        bot.answer_callback_query(c.id, "❌ Недостаточно средств.")
        return

    user["balance"] -= car_data["price"]
    user["cars"].append(f"{brand} {model}")
    update_user(c.from_user.id, user)

    bot.edit_message_text(
        f"✅ Ты купил {brand} {model} за {car_data['price']}₽!\n"
        f"💼 Новый баланс: {user['balance']}₽",
        chat_id=c.message.chat.id,
        message_id=c.message.message_id
    )

bot.polling()
