import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")
CHANNEL_USERNAME = "@newcastlecity1"

# === БАЗА ДАННЫХ (ФАЙЛЫ) ===
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
        users[user_id] = {"balance": 1000, "cars": []}
        save_users(users)
    return users[user_id]

def update_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

# === ПРОВЕРКА ПОДПИСКИ ===
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# === КОМАНДА /START ===
@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub"))
        bot.send_message(message.chat.id, "❗ Подпишись на канал для доступа к боту.", reply_markup=markup)
        return

    # Главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚗 Автосалон", "🚘 Гараж")
    markup.row("💼 Профиль")

    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"👤 {message.from_user.first_name}\n💼 Баланс: {user['balance']}₽",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub(c):
    if is_subscribed(c.from_user.id):
        bot.delete_message(c.message.chat.id, c.message.message_id)
        start(c.message)
    else:
        bot.answer_callback_query(c.id, "❌ Подпишись сначала!")

# === СЛОВАРЬ МАШИН ===
cars = {
    "BMW": [
        {"model": "BMW M5", "price": 500},
        {"model": "BMW X6", "price": 700}
    ],
    "Mercedes": [
        {"model": "Mercedes E63", "price": 800},
        {"model": "Mercedes GLE", "price": 1000}
    ]
}

# === МЕНЮ ===
@bot.message_handler(func=lambda msg: msg.text in ["🚗 Автосалон", "🚘 Гараж", "💼 Профиль"])
def menu(msg):
    user = get_user(msg.from_user.id)

    if msg.text == "🚗 Автосалон":
        markup = types.InlineKeyboardMarkup()
        for brand in cars:
            markup.add(types.InlineKeyboardButton(brand, callback_data=f"brand_{brand}"))
        bot.send_message(msg.chat.id, "Выбери марку:", reply_markup=markup)

    elif msg.text == "🚘 Гараж":
        if not user["cars"]:
            bot.send_message(msg.chat.id, "🚘 У тебя нет машин.")
        else:
            text = "🚘 Твой гараж:\n" + "\n".join(user["cars"])
            bot.send_message(msg.chat.id, text)

    elif msg.text == "💼 Профиль":
        bot.send_message(msg.chat.id, f"👤 {msg.from_user.first_name}\n💰 Баланс: {user['balance']}₽")

# === ВЫБОР МАРКИ ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("brand_"))
def show_models(c):
    brand = c.data.split("_")[1]
    markup = types.InlineKeyboardMarkup()
    for car in cars[brand]:
        cb_data = f"buy_{brand}_{car['model'].replace(' ', '_')}"
        markup.add(types.InlineKeyboardButton(f"{car['model']} - {car['price']}₽", callback_data=cb_data))
    bot.edit_message_text(
        f"🚗 {brand} — выбери модель:",
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        reply_markup=markup
    ) 
# === ПОКУПКА ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy_car(c):
    parts = c.data.split("_")
    brand = parts[1]
    model = " ".join(parts[2:])
    car_data = next((car for car in cars[brand] if car["model"] == model), None)

    if not car_data:
        bot.answer_callback_query(c.id, "Машина не найдена.")
        return

    user = get_user(c.from_user.id)

    if user["balance"] < car_data["price"]:
        bot.answer_callback_query(c.id, "❌ Недостаточно средств.")
        return

    user["balance"] -= car_data["price"]
    user["cars"].append(f"{brand} {model}")
    update_user(c.from_user.id, user)

    bot.edit_message_text(
        f"✅ Ты купил {brand} {model} за {car_data['price']}₽!\n"
        f"💼 Новый баланс: {user['balance']}₽",
        chat_id=c.message.chat.id,
        message_id=c.message.message_id
    )
import telebot from telebot import types import json import os

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")  # ЗАМЕНИ НА СВОЙ ТОКЕН

====== Работа с данными пользователей ======

def load_users(): if not os.path.exists("users.json"): with open("users.json", "w") as f: json.dump({}, f) with open("users.json", "r") as f: return json.load(f)

def save_users(users): with open("users.json", "w") as f: json.dump(users, f)

def get_user(user_id): users = load_users() user = users.get(str(user_id)) if not user: users[str(user_id)] = { "balance": 1000, "cars": [], "faction": None } save_users(users) user = users[str(user_id)] return user

def update_user(user_id, user_data): users = load_users() users[str(user_id)] = user_data save_users(users)

========== Команды и меню ==========

@bot.message_handler(commands=["start"]) def start(message): user = get_user(message.from_user.id) markup = types.ReplyKeyboardMarkup(resize_keyboard=True) markup.row("🚗 Автосалон", "🚘 Гараж") markup.row("💼 Профиль", "📘 Фракция") bot.send_message(message.chat.id, f"👋 Привет, ты попал в игру Newcastle City!", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "💼 Профиль") def profile(message): user = get_user(message.from_user.id) bot.send_message(message.chat.id, f"👤 {message.from_user.first_name}\n💼 Баланс: {user['balance']}₽")

@bot.message_handler(func=lambda msg: msg.text == "🚘 Гараж") def garage(message): user = get_user(message.from_user.id) if not user["cars"]: bot.send_message(message.chat.id, "🚗 У тебя нет машин.") else: cars_text = "\n".join(user["cars"]) bot.send_message(message.chat.id, f"🚘 Твой гараж:\n{cars_text}")

========== Фракции ==========

@bot.message_handler(func=lambda msg: msg.text == "📘 Фракция") def faction_menu(message): user = get_user(message.from_user.id) faction = user.get("faction") if not faction: return bot.send_message(message.chat.id, "❌ Ты не состоишь во фракции.")

text = f"📘 Фракция: {faction['name']}\n🎖 Ранг: {faction['rank']}"

if faction.get("is_leader"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📥 Пригласить", "🔼 Повысить", "🔽 Понизить")
    markup.row("👥 Участники", "🔙 Назад")
    return bot.send_message(message.chat.id, "👑 Панель лидера", reply_markup=markup)
else:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔙 Назад")
    return bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "👥 Участники") def show_faction_members(message): user = get_user(message.from_user.id) if not user.get("faction"): return

faction_name = user["faction"]["name"]
users = load_users()
text = f"👥 Участники фракции {faction_name}:\n"

for uid, u in users.items():
    f = u.get("faction")
    if f and f["name"] == faction_name:
        mark = "👑" if f.get("is_leader") else ""
        text += f"{mark} {uid} — ранг {f['rank']}\n"

bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text in ["📥 Пригласить", "🔼 Повысить", "🔽 Понизить"]) def handle_leader_actions(message): action = message.text prompt = { "📥 Пригласить": "📩 Введи ID пользователя для приглашения:", "🔼 Повысить": "📈 Введи ID кого повысить:", "🔽 Понизить": "📉 Введи ID кого понизить:" }[action] msg = bot.send_message(message.chat.id, prompt) bot.register_next_step_handler(msg, lambda m: process_leader_action(m, action))

def process_leader_action(message, action): user = get_user(message.from_user.id) if not user.get("faction") or not user["faction"].get("is_leader"): return bot.send_message(message.chat.id, "❌ Ты не лидер.")

try:
    target_id = int(message.text)
    target = get_user(target_id)

    if not target:
        return bot.send_message(message.chat.id, "❌ Игрок не найден.")
        if action == "📥 Пригласить":
        target["faction"] = {
            "name": user["faction"]["name"],
            "rank": 1,
            "is_leader": False
        }
        update_user(target_id, target)
        return bot.send_message(message.chat.id, "✅ Приглашён.")

    if target["faction"]["name"] != user["faction"]["name"]:
        return bot.send_message(message.chat.id, "❌ Не из твоей фракции.")

    if action == "🔼 Повысить":
        target["faction"]["rank"] += 1
    elif action == "🔽 Понизить":
        target["faction"]["rank"] = max(1, target["faction"]["rank"] - 1)

    update_user(target_id, target)
    bot.send_message(message.chat.id, "✅ Ранг обновлён.")

except:
    bot.send_message(message.chat.id, "❌ Введи корректный ID.")

@bot.message_handler(func=lambda msg: msg.text == "🔙 Назад") def back_to_main(message): markup = types.ReplyKeyboardMarkup(resize_keyboard=True) markup.row("🚗 Автосалон", "🚘 Гараж") markup.row("💼 Профиль", "📘 Фракция") bot.send_message(message.chat.id, "🔙 Главное меню", reply_markup=markup)

Запуск бота
bot.polling(none_stop=True)
