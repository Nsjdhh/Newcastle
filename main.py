import os
import sys
import telebot

# 🧪 Вывод токена (можно временно для проверки)
print("BOT_TOKEN из окружения:", os.environ.get("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds"))

# Получение токена из переменной окружения
token = os.environ.get("BOT_TOKEN")

# Проверка на отсутствие токена
if not token:
    print("❌ Переменная BOT_TOKEN не задана! Проверь Environment в Render.")
    sys.exit(1)

# Проверка на пробелы в токене
if any(char.isspace() for char in token):
    print("❌ BOT_TOKEN содержит пробелы! Удали лишние символы.")
    sys.exit(1)

# Инициализация бота
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Бот работает!")

bot.polling()
