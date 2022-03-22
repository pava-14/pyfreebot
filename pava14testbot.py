"""Задание для самостоятельной работы
1. Добавлена проверка на длину текста задачи.
    Задачи с длиной текста менее 3х символов не добавляются.
2. Добавлена команда qprint для быстрого выбора (кнопками) печати задач на сегодня или завтра

"""
from random import choice
from telebot import types
import telebot

token = '***'

bot = telebot.TeleBot(token)

RANDOM_TASKS = ['Написать Гвидо письмо', 'Выучить Python',
                'Записаться на курс в Нетологию', 'Посмотреть 4 сезон Рик и Морти']

tasks = dict()
quick_date = {
    'today': 'сегодня',
    'tomorrow': 'завтра'
}
task_min_len = 3

HELP = '''
Список доступных команд:
* print  - напечать все задачи на заданную дату
* qprint  - быстрая печать задач на сегодня или завтра
* add - добавить задачу
* random - добавить на сегодня случайную задачу
* help - Напечатать help
'''


def add_task(date, task):
    date = date.lower()

    if tasks.get(date) is not None:
        tasks[date].append(task)
    else:
        tasks[date] = [task]


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, HELP)


@bot.message_handler(commands=['random'])
def random(message):
    task = choice(RANDOM_TASKS)

    add_task('сегодня', task)

    bot.send_message(message.chat.id, f'Задача {task} добавлена на сегодня')


@bot.message_handler(commands=['add'])
def add(message):
    """Добавляет задачу в словарь.
    Выполняется проверка на длину текста задачи.
    Задачи с длиной текста менее 3х символов не добавляются.
    """
    _, date, tail = message.text.split(maxsplit=2)

    task = ' '.join([tail])

    if len(task) < task_min_len:
        msg_text = 'Задача не может быть короче 3-х символов.'
    else:
        add_task(date, task)
        msg_text = f'Задача {task} добавлена на дату {date}'

    bot.send_message(
        message.chat.id, msg_text)


def print_by_date(date_task):
    if date_task in tasks:
        current_tasks = ''
        for task in tasks[date_task]:
            current_tasks += f'[ ] {task}\n'
    else:
        current_tasks = f'На {date_task} ничего не запланировано.'

    return current_tasks


@bot.message_handler(commands=['print'])
def print(message):
    date_task = message.text.split()[1].lower()

    bot.send_message(message.chat.id, print_by_date(date_task=date_task))


@bot.message_handler(commands=['qprint'])
def menu_add(message):
    """Выводит кнопки для выбора даты печати задач на сегодня или завтра.
    """
    menu = types.InlineKeyboardMarkup()

    button_today = types.InlineKeyboardButton(
        quick_date['today'], callback_data='today')

    button_tomorrow = types.InlineKeyboardButton(
        quick_date['tomorrow'], callback_data='tomorrow')

    menu.add(button_today, button_tomorrow)

    bot.send_message(
        message.chat.id, text='Выбор даты задач:', reply_markup=menu)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Обрабатывает нажатие кнопок:

    1. Для выбора даты печати задач.
    Список задач (или сообщение об отсутствии задач) выводится вместо кнопок.
    """

    if call.message:
        if call.data in quick_date:
            date_task = quick_date[call.data]

            msg_text = f'Дела на {date_task}:\n{print_by_date(date_task=date_task)}'

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text,
                                  reply_markup=None)


bot.polling(none_stop=True)