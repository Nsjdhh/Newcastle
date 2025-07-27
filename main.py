import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")  # ЗАМЕНИ на свой токен от BotFather

# --- Функции работы с пользователями ---
def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

def get_user(uid):
    users = load_users()
    return users.get(str(uid), {"balance": 5000000, "cars": []})

def update_user(uid, data):
    users = load_users()
    users[str(uid)] = data
    save_users(users)

# --- Автосалон (машины) ---
cars = {
    "BMW": [
        {
            "model": "M5 F90",
            "price": 8000000,
            "photo": "https://i.imgur.com/xULvLWh.jpg"
        },
        {
            "model": "X6 M",
            "price": 9000000,
            "photo": "https://i.imgur.com/EWa1G8J.jpg"
        }
    ],
    "Mercedes": [
        {
            "model": "S600",
            "price": 10000000,
            "photo": "https://i.imgur.com/PKX3UTk.jpg"
        }
    ],
    "Toyota": [
        {
            "model": "Camry",
            "price": 3000000,
            "photo": "https://i.imgur.com/htqTXuO.jpg"
        }
    ]
}

# --- Команды ---
@bot.message_handler(commands=["start", "профиль"])
def profile(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"👤 {message.from_user.first_name}\n💼 Баланс: {user['balance']}₽")

@bot.message_handler(commands=["гараж"])
def garage(message):
    user = get_user(message.from_user.id)
    if not user["cars"]:
        bot.send_message(message.chat.id, "🚗 У тебя нет машин.")
    else:
        cars_text = "\n".join(user["cars"])
        bot.send_message(message.chat.id, f"🚘 Твой гараж:\n{cars_text}")

@bot.message_handler(commands=["автосалон"])
def show_brands(message):
    markup = types.InlineKeyboardMarkup()
    for brand in cars:
        markup.add(types.InlineKeyboardButton(brand, callback_data=f"brand_{brand}"))
    bot.send_message(message.chat.id, "🚗 Выбери марку машины:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("brand_"))
def show_models(callback):
    brand = callback.data.split("_")[1]
    markup = types.InlineKeyboardMarkup()
    for car in cars[brand]:
        model = car["model"]
        price = car["price"]
        cb_data = f"buy_{brand}_{model.replace(' ', '_')}"
        markup.add(types.InlineKeyboardButton(f"{model} — {price}₽", callback_data=cb_data))
    bot.edit_message_text(f"🚘 Модели {brand}:", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def show_car(callback):
    _, brand, model_raw = callback.data.split("_", 2)
    model = model_raw.replace("_", " ")
    car = next((c for c in cars[brand] if c["model"] == model), None)
    if not car:
        bot.answer_callback_query(callback.id, "❌ Машина не найдена")
        return
    caption = f"🚘 {brand} {model}\n💰 Цена: {car['price']}₽"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Купить", callback_data=f"confirm_{brand}_{model_raw}"))
    bot.send_photo(callback.message.chat.id, car["photo"], caption=caption, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def buy_car(callback):
    _, brand, model_raw = callback.data.split("_", 2)
    model = model_raw.replace("_", " ")
    car = next((c for c in cars[brand] if c["model"] == model), None)
    if not car:
        bot.answer_callback_query(callback.id, "❌ Машина не найдена")
        return

    user = get_user(callback.from_user.id)
    if user["balance"] < car["price"]:
        bot.answer_callback_query(callback.id, "❌ Недостаточно средств")
        return

    user["balance"] -= car["price"]
    user["cars"].append(f"{brand} {model}")
    update_user(callback.from_user.id, user)
    bot.send_message(callback.message.chat.id, f"✅ Ты купил {brand} {model}!\n💼 Остаток: {user['balance']}₽")

# --- Запуск бота ---
bot.polling()
