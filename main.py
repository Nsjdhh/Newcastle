import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import create_tables     # импорт функции для создания БД
from handlers import router            # импорт роутера с командами

API_TOKEN = "7646694075:AAHT0lVmi2rDDoErrCfK6uqj7T9_p74AAvQ"  # <-- ❗ Вставь сюда свой настоящий Telegram токен

# Инициализируем бота и диспетчер
bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()  # FSM в оперативной памяти
dp = Dispatcher(storage=storage)

# Подключаем роутеры (с командами, сообщениями и логикой)
dp.include_router(router)

# Главная асинхронная функция
async def main():
    await create_tables()         # создаём таблицы в базе, если их ещё нет
    print("🤖 Evolution RP бот запущен...")
    await dp.start_polling(bot)   # запускаем опрос Telegram API

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
