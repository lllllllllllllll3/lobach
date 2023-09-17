import telebot
from telebot import types
from Config import *

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    cursor.execute('SELECT id_chat FROM parents')
    if message.chat.id in list(map(lambda x: x[0], cursor.fetchall())):
        func(message)
    else:
        bot.send_message(message.chat.id, text='Вы ещё не зарегистрированы в системе'.format(message.from_user))
        reg(message)


def reg(message):
    msg = bot.send_message(message.chat.id, text='''
    Отправьте информацию по шаблону
    Фамилия Имя Отчество
    Фамилия Имя Отчество учеников через пробел
    Пароли учеников соответственно через пробел
    ''')
    bot.register_next_step_handler(msg, insert)


def insert(message):
    info = message.text.split('\n')
    if len(info) != 3:
        bot.send_message(message.chat.id, text='Вы совершили ошибку, попробуйте снова')
        reg(message)
    else:
        info.append(message.chat.id)
        cursor.execute('INSERT INTO parents (name, name_student, pasword_student, id_chat) VALUES (?, ?, ?, ?)',
                       info)
        connection.commit()
        msg = bot.send_message(message.chat.id, text='Регистрация окончена!')
        func(msg)


@bot.message_handler(content_types=['text'])
def func(message):
    bot.delete_message(message.chat.id, message.message_id)
    cursor.execute(f'SELECT name, name_student FROM parents WHERE id_chat={message.chat.id}')
    info = cursor.fetchall()
    if message.text == "/start" or message.text == 'Регистрация окончена!':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        remark = types.KeyboardButton("Замечания о поведении ученика")
        cer = types.KeyboardButton("Справки")
        markup.add(remark)
        markup.add(cer)
        bot.send_message(message.chat.id, text=f'{info[0][0]}, добро пожаловать на платформу "School Connect"',
                         reply_markup=markup)
    elif message.text == "Справки":
        msg = bot.send_message(message.chat.id, text='''Загрузите фотографию справки''')
        bot.register_next_step_handler(msg, certificate_send)
    elif message.text == "Замечания о поведении ученика":
        cursor.execute('SELECT class FROM students WHERE name=(?)', (info[0][1],))
        cursor.execute('SELECT from_, comment FROM comment_student WHERE name_student=(?) AND class_student=(?)',
                       (info[0][1], cursor.fetchall()[0][0]))
        for from1, comment in cursor.fetchall():
            bot.send_message(message.chat.id, text=f'''От {from1}
{comment}''')
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммирован..")


def certificate_send(message):
    bot.delete_message(message.chat.id, message.message_id)
    cursor.execute(f'SELECT name_student FROM parents WHERE id_chat={message.chat.id}')
    cursor.execute(f'SELECT class FROM students WHERE name=(?)', cursor.fetchall()[0])
    cursor.execute(f'SELECT name FROM teacher WHERE class_guide=(?)', cursor.fetchall()[0])
    photo = max(message.photo, key=lambda x: x.height)
    print(photo.file_id)
    cursor.execute('INSERT INTO certificates (name_teacher, certificate) VALUES (?, ?)',
                   (cursor.fetchall()[0][0], photo.file_id))
    connection.commit()


bot.polling(none_stop=True)
