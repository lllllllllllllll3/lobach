import telebot
from telebot import types  # для указание типов
# УЧЕНИЧЕСКИЙ
import sqlite3
import logging

connection = sqlite3.connect('people.db3', check_same_thread=False)
cursor = connection.cursor()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

token = '6435401279:AAFVz8zjx89m0ynNpXdpwigJoQbezq_XMPc'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    cursor.execute('SELECT id_chat FROM students')
    if message.chat.id in list(map(lambda x: x[0], cursor.fetchall())):
        func(message)
    else:
        bot.send_message(message.chat.id, text='Вы ещё не зарегистрированы в системе'.format(message.from_user))
        reg(message)


def reg(message):
    msg = bot.send_message(message.chat.id,
                           text='''Отправьте информацию по шаблону
    Фамилия Имя Отчество
    Класс
    Придумайте пароль для подключения родителя''')
    bot.register_next_step_handler(msg, insert)


def insert(message):
    info = message.text.split('\n')
    if len(info) != 3:
        bot.send_message(message.chat.id, text='Вы совершили ошибку, попробуйте снова')
        reg(message)
    else:
        info.append(message.chat.id)
        cursor.execute('INSERT INTO students (name, class, password, id_chat) VALUES (?, ?, ?, ?)', info)
        connection.commit()
        msg = bot.send_message(message.chat.id, text='Регистрация окончена, добро пожаловать!')
        func(msg)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Уже зарегестрирован" or message.text == '/start' \
            or message.text == 'Регистрация окончена, добро пожаловать!':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Расписание уроков")
        btn3 = types.KeyboardButton("Отзыв об учителе")
        markup.add(btn1, btn3)
        bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)

    elif message.text == "Расписание уроков":
        bot.send_message(message.chat.id, "физика, информатика, алгебра, алгебра, геометрия")

    elif message.text == "Отзыв об учителе":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button2 = types.KeyboardButton("Комментарий по работе")
        markup.add(button2)
        bot.send_message(message.chat.id, text=",,,", reply_markup=markup)

    elif message.text == "Комментарий по работе":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btncomm1 = types.KeyboardButton("Положительный")
        btncomm2 = types.KeyboardButton("Отрицательный")
        markup.add(btncomm1, btncomm2)
        bot.send_message(message.chat.id, text="...", reply_markup=markup)

    elif message.text == "Положительный":
        msg1 = bot.send_message(message.chat.id, text="Напишите ФИО учителя")
        msg = bot.send_message(message.chat.id,
                               text="1. Какие качества в учителе и его уроках привлекают ваше внимание и мотивируют вас учиться лучше? "
                                    "2. Какую роль играет ваш учитель в вашем процессе обучения и достижении успехов? "
                                    "3. Какие особенности и методы преподавания вашего учителя помогают вам лучше понять материал? "
                                    "4. Какая поддержка и обратная связь от вашего учителя помогает вам прогрессировать в учебе? "
                                    "5. Какие аспекты уроков вы считаете наиболее интересными и позволяющими расширить свои знания?")
        bot.register_next_step_handler(msg, insert)

    elif message.text == "Отрицательный":
        msg1 = bot.send_message(message.chat.id, text="Напишите ФИО учителя ")
        bot.register_next_step_handler(msg1, insert)
        msg = bot.send_message(message.chat.id,
                               text="1. Какие недостатки или проблемы вы видите в методах преподавания вашего учителя? "
                                    "2. В чем заключается слабая сторона вашего учителя, которая мешает вам полностью понять и усвоить предмет? "
                                    "3. Какие трудности вы испытываете в процессе обучения, и как ваш учитель не помогает в их преодолении? "
                                    "4. Какая критика или обратная связь вы хотели бы дать вашему учителю относительно его способов обучения? "
                                    "5. Какие аспекты уроков приводят к отсутствию интереса или мотивации у вас?")
        bot.register_next_step_handler(msg, insert)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммирован..")


bot.polling(none_stop=True)
