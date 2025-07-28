import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")  # 🔧 ЗАМЕНИ на свой токен

# === ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ===
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def get_user(user_id):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {"balance": 10000000, "cars": []}  # Стартовые данные
        save_users(users)
    return users[user_id]

def update_user(user_id, user_data):
    users = load_users()
    users[str(user_id)] = user_data
    save_users(users)

# === СПИСОК АВТО ===
cars = {
    "BMW": [
        {"model": "BMW M5 F90", "price": 7000000},
        {"model": "BMW X5", "price": 5500000}
    ],
    "Mercedes": [
        {"model": "Mercedes E63", "price": 8000000},
        {"model": "Mercedes G63", "price": 9000000}
    ],
    "Toyota": [
        {"model": "Toyota Camry", "price": 3000000},
        {"model": "Toyota Land Cruiser", "price": 6500000}
    ]
}

# === КОМАНДА /start и меню ===
@bot.message_handler(commands=["start", "профиль"])
def profile(message):
    user = get_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚗 Автосалон", "🚘 Гараж")
    markup.row("💼 Профиль")
    bot.send_message(
        message.chat.id,
        f"👤 {message.from_user.first_name}\n💼 Баланс: {user['balance']}₽",
        reply_markup=markup
    )

# === КНОПКИ МЕНЮ ===
@bot.message_handler(func=lambda m: m.text == "🚗 Автосалон")
def open_autosalon(message):
    show_brands(message)

@bot.message_handler(func=lambda m: m.text == "🚘 Гараж")
def open_garage(message):
    garage(message)

@bot.message_handler(func=lambda m: m.text == "💼 Профиль")
def open_profile(message):
    profile(message)

# === ГАРАЖ ===
def garage(message):
    user = get_user(message.from_user.id)
    if not user["cars"]:
        bot.send_message(message.chat.id, "🚗 У тебя нет машин.")
    else:
        cars_text = "\n".join(user["cars"])
        bot.send_message(message.chat.id, f"🚘 Твой гараж:\n{cars_text}")

# === АВТОСАЛОН: выбор бренда ===
@bot.message_handler(commands=["автосалон"])
def show_brands(message):
    markup = types.InlineKeyboardMarkup()
    for brand in cars:
        markup.add(types.InlineKeyboardButton(brand, callback_data=f"brand_{brand}"))
    bot.send_message(message.chat.id, "🚗 Выбери марку машины:", reply_markup=markup)

# === МОДЕЛИ выбранного бренда ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("brand_"))
def show_models(callback):
    brand = callback.data.split("_")[1]
    markup = types.InlineKeyboardMarkup()
    for car in cars[brand]:
        model = car["model"]
        price = car["price"]
        cb_data = f"buy_{brand}_{model.replace(' ', '_')}"
        markup.add(types.InlineKeyboardButton(f"{model} — {price}₽", callback_data=cb_data))
    bot.send_message(callback.message.chat.id, f"🚘 Модели {brand}:", reply_markup=markup)

# === ПОКУПКА машины ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy_car(callback):
    user_id = callback.from_user.id
    user = get_user(user_id)

    data = callback.data.split("_")
    brand = data[1]
    model = "_".join(data[2:]).replace('_', ' ')

    car_info = next((car for car in cars[brand] if car["model"] == model), None)
    if not car_info:
        bot.answer_callback_query(callback.id, "❌ Машина не найдена.")
        return

    price = car_info["price"]
    balance = user["balance"]

    if balance < price:
        bot.answer_callback_query(callback.id, "❌ Недостаточно денег для покупки.")
        return

    # ✅ Защита от минуса
    new_balance = balance - price
    if new_balance < 0:
        bot.answer_callback_query(callback.id, "❌ Ошибка! Баланс не может быть отрицательным.")
        return

    # 💾 Сохраняем
    user["balance"] = new_balance
    user["cars"].append(f"{brand} {model}")
    update_user(user_id, user)

    bot.answer_callback_query(callback.id, f"✅ Куплено: {brand} {model} за {price}₽")
    bot.send_message(callback.message.chat.id, f"🚗 Ты купил {brand} {model}!\n💼 Остаток: {user['balance']}₽")
import telebot

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")

# 🔹 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привет! Я бот.")

# 🔹 Команда /myid — показывает твой Telegram ID
@bot.message_handler(commands=['myid'])
def myid(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"🆔 Твой Telegram ID: {user_id}")

# 🔹 Не забудь polling

# === СТАРТ БОТА ===
bot.polling(none_stop=True)
