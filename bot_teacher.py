import telebot
from telebot import types
from Config import *

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    cursor.execute('SELECT id_chat FROM teacher')
    if message.chat.id in list(map(lambda x: x[0], cursor.fetchall())):
        func(message)
    else:
        bot.send_message(message.chat.id, text='Вы ещё не зарегистрированы в системе'.format(message.from_user))
        reg(message)


def reg(message):
    msg = bot.send_message(message.chat.id, text='''
    Отправьте информацию по шаблону (буква класса латиницей, если чего-то из перечисленного нет, поставьте минус)
    Фамилия Имя Отчество
    Классы в которых вы преподаёте
    (перечислите разделяя пробелами)
    Класс которым вы руководите
    Какой урок вы ведёте или какую должность вы занимаете?
    Рабочая почта
    ''')
    bot.register_next_step_handler(msg, insert)


def insert(message):
    info = message.text.split('\n')
    info.append(message.chat.id)
    try:
        cursor.execute('INSERT INTO teacher (name, classes, class_guide, lesson, email, id_chat) VALUES (?, ?, ?, '
                        '?, ?, ?)', info)
    except sqlite3.Error:
        bot.send_message(message.chat.id, 'Вы совершили ошибку, попробуйте снова')
        reg(message)
    connection.commit()
    msg = bot.send_message(message.chat.id, text='Регистрация окончена!')
    func(msg)


@bot.message_handler(content_types=['text'])
def func(message):
    bot.delete_message(message.chat.id, message.message_id)
    cursor.execute(f'SELECT name, class_guide FROM teacher WHERE id_chat={message.chat.id}')
    info = cursor.fetchall()
    if message.text == "/start" or message.text == 'Регистрация окончена!':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        remark = types.KeyboardButton("Замечание о поведении ученика")
        cer = types.KeyboardButton("Справки")
        markup.add(remark)
        if info[0][1] != '-':
            markup.add(cer)
        bot.send_message(message.chat.id, text=f'{info[0][0]}, добро пожаловать на платформу "School Connect"', reply_markup=markup)
    elif message.text == "Замечание о поведении ученика":
        msg = bot.send_message(message.chat.id, text='''Заполните замечание по форме (буква класса латиницей)
        Фамилия Имя Отчество ученика
        Класс ученика
        Замечание''')
        bot.register_next_step_handler(msg, remark_send)
    elif message.text == "Справки":
        try:
            cursor.execute('SELECT certificate FROM certificates WHERE name_teacher=(?)', (info[0][0],))
        except sqlite3.Error:
            bot.send_message(message.chat.id, 'Нет справок')
        for photo1 in cursor.fetchall()[0]:
            bot.send_photo(message.chat.id, photo=photo1)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммирован..")


def remark_send(message):
    bot.delete_message(message.chat.id, message.message_id)
    try:
        cursor.execute(f'SELECT name FROM teacher WHERE id_chat={message.chat.id}')
    except sqlite3.Error:
        bot.send_message(message.chat.id, 'Вы совершили ошибку, попробуйте снова')
    info = message.text.split('\n')
    info.append(cursor.fetchall()[0][0])
    try:
        cursor.execute('INSERT INTO comment_student (name_student, class_student, comment, from_) VALUES (?, ?, ?, ?)',
                       info)
        connection.commit()
        bot.send_message(message.chat.id, "Замечание отправлено")
        cursor.execute('SELECT id_chat FROM teacher WHERE class_guide=(?)', (info[1],))
        bot.send_message(cursor.fetchall()[0][0], f'На кого: {info[0]}\nОт кого: {info[-1]}\n{info[-2]}')
        cursor.execute('SELECT password FROM students WHERE name=(?) and class=(?)', info[:2])
        cursor.execute('SELECT id_chat FROM parents WHERE name_student=(?) and pasword_student=(?)',
                       (info[0], cursor.fetchall()[0][0]))
        bot.send_message(cursor.fetchall()[0][0], f'На кого: {info[0]}\nОт кого: {info[-1]}\n{info[-2]}')
    except sqlite3.Error:
        bot.send_message(message.chat.id, 'Вы совершили ошибку, попробуйте снова')


bot.polling(none_stop=True)
