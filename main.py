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
bot.polling() import os
import json
import random
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ======= БАЛАНС =========

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
    return users.get(str(user_id), 1000)

def update_balance(user_id, new_balance):
    users = load_users()
    users[str(user_id)] = new_balance
    save_users(users)

# ======= КОМАНДА /profile =======

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    balance = get_balance(user_id)
    await update.message.reply_text(f"💼 Твой баланс: {balance}₽")

# ======= КОМАНДА /casino =======

async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Введи сумму ставки:")

    return await context.user_data.update({"waiting_bet": True})

# ======= ОБРАБОТКА ЧИСЛА =======

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_bet"):
        user_id = update.message.from_user.id
        try:
            bet = int(update.message.text)
            balance = get_balance(user_id)

            if bet <= 0:
                await update.message.reply_text("❌ Ставка должна быть больше 0.")
                return
            if bet > balance:
                await update.message.reply_text("❌ У тебя недостаточно денег.")
                return

            symbols = ['🍒', '🍋', '💎', '7️⃣', '🔔']
            s1, s2, s3 = random.choices(symbols, k=3)
            result = f"{s1} | {s2} | {s3}"

            if s1 == s2 == s3:
                win = bet * 3
                balance += win
                text = f"🎉 Ты выиграл {win}₽!\n{result}"
            else:
                balance -= bet
                text = f"😢 Ты проиграл {bet}₽.\n{result}"

            update_balance(user_id, balance)

            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎰 Играть снова", callback_data="casino_again")]
            ])

            await update.message.reply_text(f"{text}\n💼 Баланс: {balance}₽", reply_markup=markup)
            context.user_data["waiting_bet"] = False

        except ValueError:
            await update.message.reply_text("❌ Введи число.")
    else:
        await update.message.reply_text("⚠️ Неизвестная команда. Напиши /casino чтобы начать игру.")

# ======= КНОПКА "ИГРАТЬ СНОВА" =======

async def casino_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["waiting_bet"] = True
    await query.message.reply_text("💰 Введи сумму ставки:")

# ======= ЗАПУСК БОТА =======

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("casino", casino))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(casino_again, pattern="casino_again"))

app.run_polling()
