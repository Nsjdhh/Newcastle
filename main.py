import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")  # <-- замени на свой токен

# 📁 Создание users.json
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

# 📦 Работа с пользователями
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
        users[user_id] = {"balance": 0, "cars": [], "quests": {}}
        save_users(users)
    return users[user_id]

def update_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

# 📲 Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚗 Автосалон", "🚘 Гараж")
    markup.row("💼 Профиль", "🎯 Квест")

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в Newcastle City 🌆\nВыбери кнопку ниже, чтобы начать!",
        reply_markup=markup
    )

# 💼 Профиль
@bot.message_handler(func=lambda msg: msg.text == "💼 Профиль")
def profile(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"👤 Игрок: {message.from_user.first_name}\n💰 Баланс: {user['balance']}₽")

# 🚘 Гараж
@bot.message_handler(func=lambda msg: msg.text == "🚘 Гараж")
def garage(message):
    user = get_user(message.from_user.id)
    if not user["cars"]:
        bot.send_message(message.chat.id, "🚗 У тебя пока нет машин.")
    else:
        cars = "\n".join(user["cars"])
        bot.send_message(message.chat.id, f"🚘 Твой гараж:\n{cars}")

# 🎯 Квест (первый простой)
@bot.message_handler(func=lambda msg: msg.text == "🎯 Квест")
def quest_handler(message):
    user = get_user(message.from_user.id)
    if user["quests"].get("first_job"):
        bot.send_message(message.chat.id, "✅ Ты уже прошёл этот квест.")
    else:
        user["balance"] += 500
        user["quests"]["first_job"] = True
        update_user(message.from_user.id, user)
        bot.send_message(message.chat.id, "🎉 Ты поработал доставщиком еды и заработал 500₽!")

bot.polling(none_stop=True)
