from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

API_TOKEN = '7646694075:AAHT0lVmi2rDDoErrCfK6uqj7T9_p74AAvQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Состояния для FSM
class PassportState(StatesGroup):
    wait_for_first_name = State()
    wait_for_last_name = State()
    wait_for_age = State()
    wait_for_city = State()

# Старт
@dp.message(commands=["start"])
async def cmd_start(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отправиться в правительство", callback_data="go_to_gov")]
        ]
    )
    await message.answer("🏙 Welcome to Evolution!\n\nЧтобы начать, вам нужно получить паспорт.\n\n⬇ Нажмите ниже:", reply_markup=keyboard)

# Обработка кнопки "Отправиться в правительство"
@dp.callback_query(lambda c: c.data == "go_to_gov")
async def go_to_government(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🚕 Вы отправились в правительство...\n⏳ Это займёт 2 минуты.")
    await asyncio.sleep(120)
    await callback.message.answer("🏛 Вы прибыли в здание правительства.\nДавайте оформим паспорт.\n\nВведите ваше *имя*:")
    await state.set_state(PassportState.wait_for_first_name)

# Имя
@dp.message(PassportState.wait_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введите вашу *фамилию*:")
    await state.set_state(PassportState.wait_for_last_name)

# Фамилия
@dp.message(PassportState.wait_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введите ваш *возраст*:")
    await state.set_state(PassportState.wait_for_age)

# Возраст
@dp.message(PassportState.wait_for_age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите *город рождения*:")
    await state.set_state(PassportState.wait_for_city)

# Город
@dp.message(PassportState.wait_for_city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()

    passport_text = (
        f"🪪 *Ваш Паспорт*\n\n"
        f"👤 Имя: {data['first_name']} {data['last_name']}\n"
        f"🎂 Возраст: {data['age']}\n"
        f"🏙️ Город рождения: {data['city']}\n"
        f"🕹 Добро пожаловать в Evolution!"
    )

    await message.answer(passport_text, parse_mode="Markdown")
    await state.clear()
