import os
import time
import threading
from telebot import TeleBot, types

bot = TeleBot(os.getenv("8045858681:AAE5X-WBhgFkwcKSvLfeHYWGqAWCB6RCdds"))

users = {}

jobs = {
    "🧹 Дворник": {"salary": 40000, "cd": 10, "time": 10},
    "🚴 Курьер": {"salary": 100000, "cd": 20, "time": 15},
    "🚕 Таксист": {"salary": 120000, "cd": 23, "time": 20},
    "👷 Строитель": {"salary": 200000, "cd": 70, "time": 30}
}

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    users.setdefault(uid, {"money": 0, "last_work": {}})
    bot.send_message(uid, "Привет! Напиши /work чтобы начать работать.")

@bot.message_handler(commands=['work'])
def choose_work(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for job in jobs:
        markup.add(job)
    bot.send_message(message.chat.id, "Выбери работу:", reply_markup=markup)

def finish_work(uid, chat_id, job):
    data = jobs[job]
    users[uid]['money'] += data['salary']
    users[uid]['last_work'][job] = time.time()
    bot.send_message(chat_id, f"✅ Работа {job} завершена!\n💰 Вы получили {data['salary']:,}₽\n💼 Баланс: {users[uid]['money']:,}₽")

@bot.message_handler(func=lambda message: message.text.strip() in jobs)
def start_job(message):
    uid = str(message.from_user.id)
    job = message.text.strip()
    now = time.time()

    if job not in users[uid]['last_work']:
        users[uid]['last_work'][job] = 0

    diff = now - users[uid]['last_work'][job]
    cd = jobs[job]['cd']

    if diff < cd:
        wait = int(cd - diff)
        return bot.send_message(message.chat.id, f"⏳ Подожди {wait} секунд перед повторной работой.")

    work_time = jobs[job]['time']
    bot.send_message(message.chat.id, f"🔨 Вы начали работать {job}... Ожидайте {work_time} сек.")

    threading.Timer(work_time, finish_work, args=[uid, message.chat.id, job]).start()

bot.polling()
