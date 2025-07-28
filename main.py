import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")

# Создание файла, если не существует
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

# Загрузка пользователей
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

# Сохранение пользователей
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# Получить данные пользователя
def get_user(user_id):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {"balance": 0, "cars": []}
        save_users(users)
    return users[user_id]

# Обновить данные пользователя
def update_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)
    @bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚗 Автосалон", "🚘 Гараж")
    markup.row("💼 Профиль")

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в КРМП проект Newcastle City!",
        reply_markup=markup
        @bot.message_handler(func=lambda message: message.text == "💼 Профиль")
def profile(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"👤 Имя: {message.from_user.first_name}\n💰 Баланс: {user['balance']}₽")
    )
    # Список машин — можно расширить
cars = {
    "Toyota": [
        {"model": "Camry", "price": 1500000, "photo": "https://example.com/toyota_camry.jpg"},
        {"model": "Corolla", "price": 1200000, "photo": "https://example.com/toyota_corolla.jpg"}
    ],
    "BMW": [
        {"model": "X5", "price": 4500000, "photo": "https://example.com/bmw_x5.jpg"},
        {"model": "M3", "price": 6000000, "photo": "https://example.com/bmw_m3.jpg"}
    ]
}

@bot.message_handler(func=lambda message: message.text == "🚗 Автосалон")
def show_brands(message):
    markup = types.InlineKeyboardMarkup()
    for brand in cars.keys():
        markup.add(types.InlineKeyboardButton(text=brand, callback_data=f"brand_{brand}"))
    bot.send_message(message.chat.id, "🚗 Выберите марку машины:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("brand_"))
def show_models(call):
    brand = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup()
    for car in cars[brand]:
        model = car["model"]
        price = car["price"]
        cb_data = f"buy_{brand}_{model.replace(' ', '_')}"
        markup.add(types.InlineKeyboardButton(text=f"{model} — {price}₽", callback_data=cb_data))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"🚗 Модели {brand}:", reply_markup=markup)
    @bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_car(call):
    user = get_user(call.from_user.id)
    data = call.data.split("_")
    brand = data[1]
    model = data[2].replace('_', ' ')

    # Найдём машину в списке
    car = next((c for c in cars[brand] if c["model"] == model), None)
    if car is None:
        bot.answer_callback_query(call.id, "Ошибка: машина не найдена.")
        return

    price = car["price"]
    if user["balance"] < price:
        bot.answer_callback_query(call.id, "Недостаточно денег для покупки.")
        return

    # Списываем деньги и добавляем машину в гараж
    user["balance"] -= price
    user["cars"].append(f"{brand} {model}")
    update_user(call.from_user.id, user)

    bot.answer_callback_query(call.id, f"Вы успешно купили {brand} {model} за {price}₽!")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"🎉 Вы купили {brand} {model}!\n💰 Остаток баланса: {user['balance']}₽")
    @bot.message_handler(func=lambda message: message.text == "🚘 Гараж")
def garage(message):
    user = get_user(message.from_user.id)
    if not user["cars"]:
        bot.send_message(message.chat.id, "🚗 У тебя нет машин в гараже.")
    else:
        cars_list = "\n".join(user["cars"])
        bot.send_message(message.chat.id, f"🚘 Твой гараж:\n{cars_list}")
        bot.polling(none_stop=True)
    
