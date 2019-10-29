import telebot
import psycopg2
import re

bot = telebot.TeleBot('923254931:AAE-jtEP5nZv8WhLUL5PBPy-TTkRG9Ew4V0')
conn = psycopg2.connect(dbname='d9gqs0c8qluemb', user='rfyglxtwtqlzun',
                        host='ec2-174-129-231-116.compute-1.amazonaws.com',
                        password='38ae72b269ce6d2ed66524d4ece1fb3ba412f380c22128f27a7f3ee780465524')
cursor = conn.cursor()
number = ''

cursor.execute("SELECT region, sity from public.\"apartaments\" GROUP BY region, sity;")
regions = cursor.fetchall()
print(regions)
for region in regions:
    print(region[0])
    print(region[1])


@bot.message_handler(commands=['start', 'help', 'number', 'realty'])
def handle_start_help(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, 'Привет, я бот, который проверяет агента по номеру телефона.\n' +
                         'Для того, чтобы узнать агент это или нет, введи /number')
        userfind = "Новый пользователь: " + str(message.from_user)
        bot.send_message(chat_id=320143245, text=userfind)
        add_user(message)

    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши /number для проверки номера телефона в базе агентов")

    elif message.text == "/number":
        bot.send_message(message.from_user.id, "Введи номер:")
        bot.register_next_step_handler(message, get_number)

    elif message.text == "/realty":
        keyboard1 = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton(text='Снять', callback_data='Снять')
        keyboard1.add(key_1)
        key_2 = telebot.types.InlineKeyboardButton(text='Купить', callback_data='Купить')
        keyboard1.add(key_2)
        key_3 = telebot.types.InlineKeyboardButton(text='Отписаться', callback_data='Отписаться')
        keyboard1.add(key_3)
        bot.send_message(message.from_user.id, "Снять или Купить?", reply_markup=keyboard1)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "Снять":
        bot.send_message(call.message.chat.id, "В разработке...")
    elif call.data == "Купить":
        keyboard2 = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton(text='Минская', callback_data='5')
        keyboard2.add(key_1)
        bot.send_message(call.message.chat.id, "Выберите область:", reply_markup=keyboard2)
    elif call.data == "5":
        keyboard3 = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton(text='Жодино', callback_data='Жодино')
        keyboard3.add(key_1)
        bot.send_message(call.message.chat.id, "Выберите город:", reply_markup=keyboard3)
    elif call.data == "Жодино":
        text = "г. Жодино"
        keyboard4 = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton(text="Да", callback_data='Save')
        keyboard4.add(key_1)
        key_2 = telebot.types.InlineKeyboardButton(text="Нет", callback_data='DontSave')
        keyboard4.add(key_2)
        bot.send_message(call.message.chat.id, text, reply_markup=keyboard4)

    elif call.data == "Save":
        id = str(call.from_user.id)
        sity = call.message.text
        cursor.execute("UPDATE public.\"botusers\" SET sity = %s WHERE userid = %s;", (sity, id))
        conn.commit()
        bot.send_message(call.message.chat.id, "Сохранил")
    elif call.data == "Отписаться":
        id = str(call.from_user.id)
        cursor.execute("UPDATE public.\"botusers\" SET sity = null WHERE userid = %s;", (id,))
        conn.commit()
        bot.send_message(call.message.chat.id, "Отписался")
    elif call.data == "DontSave":
        keyboard1 = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton(text='Снять', callback_data='Снять')
        keyboard1.add(key_1)
        key_2 = telebot.types.InlineKeyboardButton(text='Купить', callback_data='Купить')
        keyboard1.add(key_2)
        key_3 = telebot.types.InlineKeyboardButton(text='Отписаться', callback_data='Отписаться')
        keyboard1.add(key_3)
        bot.send_message(call.message.chat.id, "Снять или Купить?", reply_markup=keyboard1)


def add_user(message):
    params = (message.from_user.id, message.from_user.first_name, message.from_user.last_name,
              message.from_user.username)
    id = str(message.from_user.id)
    cursor.execute("SELECT * from public.\"botusers\" WHERE userid = %s;", (id,))
    rows = cursor.fetchall()
    if not rows:
        cursor.execute("INSERT INTO public.\"botusers\"(userid, firstname, lastname, username, sity) "
                       "VALUES(%s, %s, %s, %s, null);", (params))
    else:
        print("User exist")
    conn.commit()


def get_number(message):
    userfind = "Пользователь: " + str(message.from_user) + " Ищет " + message.text
    bot.send_message(chat_id=320143245, text=userfind)
    global number
    number = '%' + message.text + '%'
    number = re.sub(r'-|\(|\)|\s', '', number)
    if message.text != "/number" and message.text != "/help" and message.text != "/start":
        if len(number) > 6:
            cursor.execute("SELECT order_number, order_who, order_number_name FROM public.\"Agents\" "
                           "WHERE order_number LIKE %s;", (number,))
            mobile_records = cursor.fetchall()
            if mobile_records:
                for row in mobile_records:
                    prname = ''
                    prnumber = str(row[0])

                    if row[1] != "None":
                        pragent = " " + row[1]
                        message_text = pragent

                    else:
                        if row[2] != "None":
                            prname = " " + row[2]
                        odds = 50
                        if row[2] != "None":
                            prname = " " + row[2]
                        message_text = "Агент" + prname + " с номером " + prnumber + " с вероятностью " + \
                                       str(odds) + " %"
                    bot.send_message(message.from_user.id, message_text)
                bot.register_next_step_handler(message, get_number)
            else:
                bot.send_message(message.from_user.id, "Номер не найден")
                bot.register_next_step_handler(message, get_number)

        else:
            bot.send_message(message.from_user.id, "Введите минимум 7 цифр")
            bot.register_next_step_handler(message, get_number)


bot.polling(none_stop=True, interval=0)
