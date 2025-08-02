from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import asyncio
from database import add_user, get_user

router = Router()

class PassportState(StatesGroup):
    wait_for_first_name = State()
    wait_for_last_name = State()
    wait_for_age = State()
    wait_for_city = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправиться в правительство", callback_data="go_to_gov")]
    ])
    await message.answer(
        "🏙 Welcome to Evolution!\n\nЧтобы начать, нужно получить паспорт.\nНажмите кнопку ниже.",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "go_to_gov")
async def go_to_government(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🚕 Вы отправились в правительство...\n⏳ Это займёт 2 минуты.")
    await asyncio.sleep(120)
    await callback.message.answer("🏛 Вы прибыли в правительство.\nВведите ваше имя:")
    await state.set_state(PassportState.wait_for_first_name)
    await callback.answer()  # чтобы убрать "часики" у кнопки

@router.message(PassportState.wait_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введите вашу фамилию:")
    await state.set_state(PassportState.wait_for_last_name)

@router.message(PassportState.wait_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введите ваш возраст:")
    await state.set_state(PassportState.wait_for_age)

@router.message(PassportState.wait_for_age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите числом ваш возраст.")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Введите город рождения:")
    await state.set_state(PassportState.wait_for_city)

@router.message(PassportState.wait_for_city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()

    # Сохраняем в базу
    await add_user(
        user_id=message.from_user.id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        city=data['city']
    )

    passport_text = (
        f"🪪 <b>Ваш Паспорт</b>\n\n"
        f"👤 Имя: {data['first_name']} {data['last_name']}\n"
        f"🎂 Возраст: {data['age']}\n"
        f"🏙️ Город рождения: {data['city']}\n"
        f"💰 Баланс: 5000₽\n"
        f"🕹 Добро пожаловать в Evolution RP!"
    )

    await message.answer(passport_text, parse_mode="HTML")
    await state.clear()

@router.message(Command("passport"))
async def show_passport(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Вы ещё не зарегистрированы. Напишите /start.")
        return

    user_id, first_name, last_name, age, city, balance, job, car, house = user
    text = (
        f"🪪 <b>Паспорт</b>\n\n"
        f"👤 Имя: {first_name} {last_name}\n"
        f"🎂 Возраст: {age}\n"
        f"🏙️ Город: {city}\n"
        f"💼 Работа: {job or 'Нет'}\n"
        f"🚗 Машина: {car or 'Нет'}\n"
        f"🏠 Дом: {house or 'Нет'}\n"
        f"💰 Баланс: {balance}₽"
    )
    await message.answer(text, parse_mode="HTML")
