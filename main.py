import os
import sys
import telebot

# ✅ Вывод токена из переменной окружения (для отладки)
print("BOT_TOKEN из окружения:", os.environ.get("BOT_TOKEN"))

# Получение токена из окружения
token = os.environ.get("BOT_TOKEN")

# Проверка: если токена нет — выводим ошибку
if not token:
    print("❌ Переменная BOT_TOKEN не задана! Проверь Environment в Render.")
    sys.exit(1)

# Проверка: если есть пробелы в токене — ошибка
if any(char.isspace() for char in token):
    print("❌ BOT_TOKEN содержит пробелы! Удали лишние символы.")
    sys.exit(1)

# Создаём бота
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Бот работает!")

# Запускаем бота
bot.polling() import telebot
from telebot import types
import random
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")

# 📁 Файл с балансами
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def get_balance(user_id):
    users = load_users()
    return users.get(str(user_id), 1000)  # начальный баланс 1000

def update_balance(user_id, new_balance):
    users = load_users()
    users[str(user_id)] = new_balance
    save_users(users)

# 📊 Показать баланс
@bot.message_handler(commands=['profile'])
def profile(message):
    balance = get_balance(message.from_user.id)
    bot.send_message(message.chat.id, f"💼 Твой баланс: {balance}₽")

# 🎰 Казино - просит ставку
@bot.message_handler(commands=['casino'])
def casino(message):
    msg = bot.send_message(message.chat.id, "💰 Введи сумму ставки:")
    bot.register_next_step_handler(msg, play_casino)

# 🎲 Игра
def play_casino(message):
    user_id = message.from_user.id
    try:
        bet = int(message.text)
        balance = get_balance(user_id)
        if bet <= 0:
            bot.send_message(message.chat.id, "❌ Ставка должна быть больше 0.")
            return
        if bet > balance:
            bot.send_message(message.chat.id, "❌ У тебя недостаточно денег.")
            return

        symbols = ['🍒', '🍋', '💎', '7️⃣', '🔔']
        s1 = random.choice(symbols)
        s2 = random.choice(symbols)
        s3 = random.choice(symbols)
        result = f"{s1} | {s2} | {s3}"

        if s1 == s2 == s3:
            win = bet * 3
            balance += win
            text = f"🎉 Ты выиграл {win}₽!\n{result}"
        else:
            balance -= bet
            text = f"😢 Ты проиграл {bet}₽.\n{result}"

        update_balance(user_id, balance)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎰 Играть снова", callback_data="casino_again"))
        bot.send_message(message.chat.id, f"{text}\n💼 Баланс: {balance}₽", reply_markup=markup)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число.")

# 🔁 Повторить игру
@bot.callback_query_handler(func=lambda c: c.data == "casino_again")
def again_callback(c):
    casino(c.message)

