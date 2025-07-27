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
bot.polling()

import random
from telebot import types

@bot.message_handler(commands=['casino'])
def casino(message):
    user_id = message.chat.id
    slots = ['🍒','🍋','🍇','🔔','💎']
    result = [random.choice(slots) for _ in range(3)]
    text = f"🎰 | {result[0]} | {result[1]} | {result[2]} |\n"

    if result.count(result[0]) == 3:
        text += "🎉 Джекпот! Вы выиграли 500 000₽!"
    elif len(set(result)) < 3:
        text += "😎 Победа — вы выиграли 100 000₽!"
    else:
        text += "😢 Увы, вы проиграли."

    # 📸 Отправляем картинку
    with open('slot1.png', 'rb') as photo:
        bot.send_photo(user_id, photo, caption=text)

    # 🎮 Кнопка "Играть снова"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎰 Играть снова", callback_data="play_again"))
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "play_again")
def play_again(c):
    casino(c.message)
