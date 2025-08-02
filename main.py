import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import create_tables
from handlers import router

API_TOKEN = "7646694075:AAHT0lVmi2rDDoErrCfK6uqj7T9_p74AAvQ"  # вставь сюда токен твоего бота

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(router)

async def main():
    await create_tables()          # создаём таблицы в базе, если их нет
    await dp.start_polling(bot)    # запускаем бота

if __name__ == "__main__":
    asyncio.run(main())
