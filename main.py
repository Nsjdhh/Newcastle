import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")  # ЗАМЕНИ НА СВОЙ ТОКЕН

# 📁 Инициализация users.json
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
        users[user_id] = {"balance": 0, "cars": [], "quests": {}}
        save_users(users)
    return users[user_id]

def update_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

# 🚀 Старт и приветствие
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)  # регистрация, если новый игрок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚗 Автосалон", "🚘 Гараж")
    markup.row("💼 Профиль", "📜 Инфо", "🎯 Квест")

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в *Newcastle City* — ролевой проект по типу КРМП!\n\n"
        "🎮 Здесь ты можешь покупать машины, выполнять квесты, вступать в фракции и развиваться.\n"
        "💸 Валюта: *NC (Newcastle Coin)*\n"
        "❗ Машины стоят от *5.000.000 NC* — без халявы, только честная игра.",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 💼 Профиль
@bot.message_handler(func=lambda msg: msg.text == "💼 Профиль")
def profile(message):
    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"👤 Игрок: {message.from_user.first_name}\n💰 Баланс: {user['balance']:,} NC"
    )

# 📜 Информация
@bot.message_handler(func=lambda msg: msg.text == "📜 Инфо")
def info(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ *Newcastle City* — это ролевой текстовый бот по типу КРМП.\n"
        "Ты можешь покупать авто, развиваться, вступать в фракции и выполнять миссии.\n\n"
        "🚗 Команды:\n"
        "— Автосалон: Покупка машин\n"
        "— Гараж: Просмотр машин\n"
        "— Квест: Задания\n"
        "— Профиль: Баланс и ник\n\n"
        "💰 Валюта: *NC (Newcastle Coin)*",
        parse_mode="Markdown"
    )

# 🎯 Квест (пока без награды)
@bot.message_handler(func=lambda msg: msg.text == "🎯 Квест")
def quest_handler(message):
    user = get_user(message.from_user.id)
    if user["quests"].get("intro"):
        bot.send_message(message.chat.id, "✅ Ты уже прошёл вступление.")
    else:
        user["quests"]["intro"] = True
        update_user(message.from_user.id, user)
        bot.send_message(message.chat.id, "📜 Ты прошёл вводное обучение. Вперёд к развитию!")

# 🚘 Гараж
@bot.message_handler(func=lambda msg: msg.text == "🚘 Гараж")
def garage(message):
    user = get_user(message.from_user.id)
    if not user["cars"]:
        bot.send_message(message.chat.id, "🚗 У тебя пока нет машин.")
    else:
        cars = "\n".join(user["cars"])
        bot.send_message(message.chat.id, f"🚘 Твой гараж:\n{cars}")

bot.polling(none_stop=True)
