import telebot
from telebot 
import types 
import json 
import os

TOKEN = "8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds"  # ЗАМЕНИ на свой токен бота bot = telebot.TeleBot(TOKEN)

====== База пользователей ======

if not os.path.exists("users.json"): with open("users.json", "w") as f: json.dump({}, f)

def load_users(): with open("users.json", "r") as f: return json.load(f)

def save_users(users): with open("users.json", "w") as f: json.dump(users, f, indent=4)

def get_user(user_id): users = load_users() user_id = str(user_id) if user_id not in users: users[user_id] = {"balance": 0, "cars": []} save_users(users) return users[user_id]

def update_user(user_id, data): users = load_users() users[str(user_id)] = data save_users(users)

====== Список машин ======

cars = { "BMW": [ {"model": "BMW X5", "price": 6000000, "photo": "https://cdn.motor1.com/images/mgl/0ANM8/s3/bmw-x5-m.jpg"}, {"model": "BMW M5", "price": 9000000, "photo": "https://cdn.bmwblog.com/wp-content/uploads/2021/06/2021-bmw-m5-competition-test-drive-35.jpg"}, {"model": "BMW i8", "price": 12000000, "photo": "https://cdn.motor1.com/images/mgl/W6r1v/s3/bmw-i8.jpg"} ], "Mercedes-Benz": [ {"model": "E-Class", "price": 6500000, "photo": "https://www.mercedes-benz.ru/passengercars/mercedes-benz-cars/models/e-class/sedan-v213/image-gallery/_jcr_content/media_gallery_container/par/media_gallery_item/image.MQ6.0.20230110132739.jpeg"}, {"model": "G63 AMG", "price": 16000000, "photo": "https://wroom.ru/i/cars2/mercedes_g63_amg_1.jpg"}, {"model": "S-Class", "price": 14000000, "photo": "https://upload.wikimedia.org/wikipedia/commons/f/f7/2018_Mercedes-Benz_S_560_4MATIC.jpg"} ], "Toyota": [ {"model": "Camry", "price": 3000000, "photo": "https://avatars.mds.yandex.net/get-autoru-vos/2039318/2f8b44a0b1c8f74c1fd2f4b42e0208f2/1200x900"}, {"model": "Land Cruiser 300", "price": 11500000, "photo": "https://upload.wikimedia.org/wikipedia/commons/0/05/Toyota_Land_Cruiser_300_2021.jpg"}, {"model": "Supra", "price": 8000000, "photo": "https://www.toyota.com/imgix/responsive/images/mlp/colorizer/2021/supra/3W1/1.png"} ], "Audi": [ {"model": "Audi A6", "price": 5500000, "photo": "https://cdn.motor1.com/images/mgl/l0R6z/s3/2021-audi-a6-sedan.jpg"}, {"model": "Audi RS6", "price": 12000000, "photo": "https://cdn.motor1.com/images/mgl/1M0k3/s3/2020-audi-rs6-avant.jpg"} ], "Lamborghini": [ {"model": "Huracan", "price": 23000000, "photo": "https://cdn.motor1.com/images/mgl/0ANM8/s3/lamborghini-huracan.jpg"}, {"model": "Aventador", "price": 40000000, "photo": "https://cdn.motor1.com/images/mgl/BZ3B7/s3/lamborghini-aventador-svj.jpg"} ], "Porsche": [ {"model": "911 Turbo", "price": 19000000, "photo": "https://cdn.motor1.com/images/mgl/Xe0Ae/s3/porsche-911-turbo.jpg"}, {"model": "Cayenne", "price": 11000000, "photo": "https://cdn.motor1.com/images/mgl/y3xr7/s3/2023-porsche-cayenne.jpg"} ] }

====== /start ======

@bot.message_handler(commands=["start"]) def start(message): user = get_user(message.from_user.id) markup = types.ReplyKeyboardMarkup(resize_keyboard=True) markup.row("🚗 Автосалон", "🚘 Гараж") markup.row("💼 Профиль") bot.send_message( message.chat.id, "👋 Добро пожаловать в КРМП проект - бот Newcastle City!\n🎯 В будущем тут будет квест!\nВыбери действие:", reply_markup=markup )

====== Профиль ======

@bot.message_handler(func=lambda message: message.text == "💼 Профиль") def profile(message): user = get_user(message.from_user.id) bot.send_message(message.chat.id, f"👤 {message.from_user.first_name}\n💼 Баланс: {user['balance']}₽")

====== Гараж ======

@bot.message_handler(func=lambda message: message.text == "🚘 Гараж") def garage(message): user = get_user(message.from_user.id) if not user["cars"]: bot.send_message(message.chat.id, "🚗 У тебя нет машин.") else: text = "\n".join(user["cars"]) bot.send_message(message.chat.id, f"🧾 Твои машины:\n{text}")

====== Автосалон ======

@bot.message_handler(func=lambda message: message.text == "🚗 Автосалон") def show_brands(message): markup = types.InlineKeyboardMarkup() for brand in cars: markup.add(types.InlineKeyboardButton(brand, callback_data=f"brand_{brand}")) bot.send_message(message.chat.id, "🚘 Выбери марку автомобиля:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("brand_")) def show_models(callback): brand = callback.data.split("", 1)[1] markup = types.InlineKeyboardMarkup() for car in cars[brand]: model = car["model"] price = car["price"] cb_data = f"buy{brand}{model.replace(' ', '')}" markup.add(types.InlineKeyboardButton(f"{model} — {price}₽", callback_data=cb_data)) bot.edit_message_text(f"📍 {brand}: выбери модель", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_")) def buy_car(callback): , brand, raw_model = callback.data.split("", 2) model = raw_model.replace("_", " ") user_id = str(callback.from_user.id) user = get_user(user_id)

car = next((c for c in cars[brand] if c["model"] == model), None)
if not car:
    return bot.send_message(callback.message.chat.id, "❌ Автомобиль не найден.")

if car["price"] > user["balance"]:
    return bot.send_message(callback.message.chat.id, "💸 Недостаточно средств.")

if model in user["cars"]:
    return bot.send_message(callback.message.chat.id, "🚘 У тебя уже есть этот автомобиль.")

user["balance"] -= car["price"]
user["cars"].append(model)
update_user(user_id, user)

bot.send_photo(callback.message.chat.id, car["photo"],
    caption=f"🎉 Ты купил {brand} {model} за {car['price']}₽!\n💼 Новый баланс: {user['balance']}₽")

====== Запуск ======

bot.polling(none_stop=True)

