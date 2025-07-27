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
