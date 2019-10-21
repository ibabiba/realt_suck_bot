import telebot
import psycopg2
import re

bot = telebot.TeleBot('923254931:AAE-jtEP5nZv8WhLUL5PBPy-TTkRG9Ew4V0')
conn = psycopg2.connect(dbname='d9gqs0c8qluemb', user='rfyglxtwtqlzun',
                        host='ec2-174-129-231-116.compute-1.amazonaws.com',
                        password='38ae72b269ce6d2ed66524d4ece1fb3ba412f380c22128f27a7f3ee780465524')
cursor = conn.cursor()
number = ''

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, 'Привет, я бот, который проверяет агента по номеру телефона.\n' +
                                               'Для того, чтобы узнать агент это или нет, введи /number')
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши /number для проверки номера телефона в базе агентов")
    elif message.text == "/number":
        bot.send_message(message.from_user.id, "Введи номер:")
        bot.register_next_step_handler(message, get_number)
    # else:
    #   bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

def get_number(message):
    global number
    number = '%' + message.text + '%'
    number = re.sub(r'-|\(|\)|\s', '', number)
    if len(number) > 6:
        print(number)
        cursor.execute("SELECT order_number, order_who, order_number_name FROM public.\"Agents\" WHERE order_number "
                       "LIKE %s;", (number,))
        mobile_records = cursor.fetchall()
        if mobile_records:
            for row in mobile_records:
                prname = ''
                pragent = ''
                prnumber = str(row[0])
                if row[1] != "None":
                    pragent = " " + row[1]
                    odds = 100
                else:
                    if row[2] != "None":
                        prname = " " + row[2]
                    odds = 50
                if row[2] != "None":
                    prname = " " + row[2]
                message_text = "Найден " + str(odds) + " % агент" + prname + pragent + " с номером " \
                               + prnumber
                bot.send_message(message.from_user.id, message_text)
                break
        else:
            bot.send_message(message.from_user.id, "Номер не найден")
        bot.register_next_step_handler(message, get_number)

    else:
        bot.send_message(message.from_user.id, "Введите минимум 7 цифр")
        bot.register_next_step_handler(message, get_number);

bot.polling(none_stop=True, interval=0)
