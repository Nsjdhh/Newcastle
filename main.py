import telebot
from telebot import types

bot = telebot.TeleBot("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds")
CHANNEL_USERNAME = "https://t.me/newcastlecity1"  # укажи юзернейм канала с @

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        # Статусы: "member", "creator", "administrator" считаются подписанными
        if member.status in ["member", "creator", "administrator"]:
            return True
        else:
            return False
    except Exception as e:
        # Если не удалось проверить — считаем не подписанным
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(
            message.chat.id,
            "❗️ Чтобы использовать бота, подпишись на наш канал.",
            reply_markup=markup
        )
        return

    welcome_text = (
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Ты попал в игру Newcastle City КРМП — добро пожаловать!\n\n"
        "Выбери действие из меню ниже:"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚗 Автосалон", "🚘 Гараж")
    markup.row("💼 Профиль")

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(
            message.chat.id,
            "❗️ Чтобы использовать бота, подпишись на наш канал.",
            reply_markup=markup
        )
        return

    if message.text == "🚗 Автосалон":
        bot.send_message(message.chat.id, "Открываю автосалон... (здесь будет список машин)")
    elif message.text == "🚘 Гараж":
        bot.send_message(message.chat.id, "Загружаю твой гараж... (здесь будут твои машины)")
    elif message.text == "💼 Профиль":
        bot.send_message(message.chat.id, f"Профиль пользователя {message.from_user.first_name}")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выбери действие из меню.")

bot.polling()
