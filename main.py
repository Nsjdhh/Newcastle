import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import requests

# Используем токен из переменной окружения или напрямую
API_TOKEN = os.getenv("API_TOKEN") or "7646694075:AAHT0lVmi2rDDoErrCfK6uqj7T9_p74AAvQ"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# IP-адрес
@dp.message_handler(commands=["ip"])
async def handle_ip(message: types.Message):
    ip = message.get_args()
    if not ip:
        await message.reply("❗ Используй: /ip 8.8.8.8")
        return

    r = requests.get(f"https://ipinfo.io/{ip}/json")
    data = r.json()

    response = (
        f"🌐 IP: {data.get('ip')}\n"
        f"🏙 Город: {data.get('city')}\n"
        f"🌍 Страна: {data.get('country')}\n"
        f"🏢 Организация: {data.get('org')}\n"
        f"📍 Локация: {data.get('loc')}"
    )
    await message.reply(response)

# Email
@dp.message_handler(commands=["email"])
async def handle_email(message: types.Message):
    email = message.get_args()
    if not email:
        await message.reply("❗ Используй: /email example@gmail.com")
        return

    r = requests.get(f"https://emailrep.io/{email}")
    if r.status_code != 200:
        await message.reply("⚠️ Не удалось получить данные.")
        return

    data = r.json()
    response = (
        f"📧 Email: {email}\n"
        f"Репутация: {data.get('reputation')}\n"
        f"Проверен: {data.get('suspicious')}\n"
        f"Присутствует в утечках: {data.get('references')}"
    )
    await message.reply(response)

# Телефон (заглушка)
@dp.message_handler(commands=["phone"])
async def handle_phone(message: types.Message):
    phone = message.get_args()
    if not phone:
        await message.reply("❗ Используй: /phone +71234567890")
        return

    # PhoneInfoga требует сервер, а тут простой ответ-заглушка
    await message.reply(f"📱 Поиск по номеру телефона: {phone}\n(Нужен внешний сканер — позже добавим)")

# Start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "👋 Привет! Я OSINT-бот.\n\n"
        "📌 Команды:\n"
        "/ip [IP]\n"
        "/email [почта]\n"
        "/phone [номер]"
    )

if __name__ == "__main__":
    executor.start_polling(dp)
