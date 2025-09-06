import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ----------------------
# Настройки
# ----------------------
TOKEN = os.environ.get("8138082544:AAHqJk48idUEqP2nIi-UuX9fvqLDesBeYrA")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Загружаем данные
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Игроки: user_id -> {money, job, experience, licenses, character}
users = {}

# ----------------------
# Команды
# ----------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"money":0, "job":None, "experience":0, "licenses":[], "character":None}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🧽 Спанч Боб", "⭐ Патрик", "🦀 Мистер Крабс", "🐿️ Сэнди")
    await message.reply("Привет! Выбери персонажа:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ["🧽 Спанч Боб","⭐ Патрик","🦀 Мистер Крабс","🐿️ Сэнди"])
async def choose_character(message: types.Message):
    user_id = message.from_user.id
    users[user_id]["character"] = message.text
    await message.reply(f"Вы выбрали {message.text}! Теперь выбери работу командой:\n/выбратьработу <название_работы>")

@dp.message_handler(commands=["выбратьработу"])
async def choose_job(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Укажи работу: /выбратьработу <название>")
        return
    job_name = args[1]
    if job_name not in data["jobs"]:
        await message.reply("Такой работы нет.")
        return
    users[user_id]["job"] = job_name
    await message.reply(f"Вы устроились на работу: {job_name}")

@dp.message_handler(commands=["работать"])
async def work(message: types.Message):
    user_id = message.from_user.id
    user = users.get(user_id)
    if not user or not user["job"]:
        await message.reply("Сначала выбери работу: /выбратьработу <название>")
        return

    job = data["jobs"][user["job"]]
    # Проверяем опыт
    if user["experience"] < job["requirements"]["experience_days"]:
        await message.reply(f"Требуется {job['requirements']['experience_days']} дней опыта для этой работы.")
        return
    # Проверяем лицензию
    license_needed = job["requirements"]["license"]
    if license_needed and license_needed not in user["licenses"]:
        await message.reply(f"Для этой работы нужна лицензия: {license_needed}")
        return

    user["money"] += job["salary_day"]
    user["experience"] += 1
    await message.reply(f"Вы отработали день! Заработано: {job['salary_day']} ₽\nВсего денег: {user['money']} ₽\nОпыт: {user['experience']} дней.")

@dp.message_handler(commands=["баланс"])
async def balance(message: types.Message):
    user_id = message.from_user.id
    user = users.get(user_id)
    if not user:
        await message.reply("Ты еще не начал игру: /start")
        return
    await message.reply(f"У тебя {user['money']} ₽")

@dp.message_handler(commands=["купитьлицензию"])
async def buy_license(message: types.Message):
    user_id = message.from_user.id
    user = users.get(user_id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Укажи лицензию: /купитьлицензию <название>")
        return
    license_name = args[1]
    if license_name not in data["licenses"]:
        await message.reply("Такой лицензии нет.")
        return
    price = data["licenses"][license_name]
    if user["money"] < price:
        await message.reply(f"Недостаточно денег. Цена: {price} ₽")
        return
    user["money"] -= price
    user["licenses"].append(license_name)
    await message.reply(f"Лицензия {license_name} куплена! Остаток: {user['money']} ₽")

@dp.message_handler(commands=["машины"])
async def list_cars(message: types.Message):
    text = "Доступные машины:\n"
    for car, price in data["cars"].items():
        text += f"{car} — {price} ₽\n"
    await message.reply(text)

@dp.message_handler(commands=["купитьмашину"])
async def buy_car(message: types.Message):
    user_id = message.from_user.id
    user = users.get(user_id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Укажи машину: /купитьмашину <название>")
        return
    car_name = args[1]
    if car_name not in data["cars"]:
        await message.reply("Такой машины нет.")
        return
    price = data["cars"][car_name]
    if user["money"] < price:
        await message.reply(f"Недостаточно денег. Цена: {price} ₽")
        return
    user["money"] -= price
    user.setdefault("cars_owned", []).append(car_name)
    await message.reply(f"Вы купили {car_name}! Остаток: {user['money']} ₽")

# ----------------------
# Запуск
# ----------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
