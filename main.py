   # Copyright 2023 Matvei Belonogov

   # Licensed under the Apache License, Version 2.0 (the "License");
   # you may not use this file except in compliance with the License.
   # You may obtain a copy of the License at

   #     http://www.apache.org/licenses/LICENSE-2.0

   # Unless required by applicable law or agreed to in writing, software
   # distributed under the License is distributed on an "AS IS" BASIS,
   # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   # See the License for the specific language governing permissions and
   # limitations under the License.

import datetime
import telebot
import gspread
from google.oauth2.service_account import Credentials

# Замените следующие строки своими данными
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
GOOGLE_JSON_FILE = 'path/to/your/google-credentials.json'
GOOGLE_SHEET_ID_1 = 'YOUR_GOOGLE_SHEET_ID_FOR_CAMPUS_1'  # 1 корпус
GOOGLE_SHEET_ID_2 = 'YOUR_GOOGLE_SHEET_ID_FOR_CAMPUS_2'  # 2 корпус

# Инициализируем телеграм-бота
bot = telebot.TeleBot(BOT_TOKEN)

# Список допустимых user_ids
ALLOWED_USER_IDS = [ENTER_ALLOWED_USER_IDS]


# Функция для проверки идентификатора пользователя
def is_allowed_user(user_id):
    return user_id in ALLOWED_USER_IDS


# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if not is_allowed_user(user_id):
        bot.send_message(message.chat.id, "Извините, у вас нет доступа для использования этого бота.")
        return

    bot.send_message(message.chat.id, "Привет!\n "
                                      "С помощью этого бота вы сможете подать заявку в школьную столовую!")
    ask_class(message)


# Функция для команды /neworder
@bot.message_handler(commands=['neworder'])
def handle_new_order(message):
    user_id = message.from_user.id
    if not is_allowed_user(user_id):
        bot.send_message(message.chat.id, "Извините, у вас нет доступа для создания заявки.")
        return

    ask_class(message)


# Функция для запроса номера класса
def ask_class(message):
    bot.send_message(message.chat.id, "Введите номер класса (например, 2Б):")
    bot.register_next_step_handler(message, process_class)


# Функция для обработки ответа с номером класса
def process_class(message):
    class_number = message.text
    ask_campus(message, class_number)


# Функция для запроса корпуса
def ask_campus(message, class_number):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("1 корпус", "2 корпус")
    bot.send_message(message.chat.id, "Выберите корпус:", reply_markup=keyboard)
    bot.register_next_step_handler(message, process_campus, class_number)


# Функция для обработки ответа с корпусом
def process_campus(message, class_number):
    campus = message.text

    # Убираем клавиатуру после выбора корпуса
    bot.send_message(message.chat.id, "Вы выбрали: " + campus, reply_markup=telebot.types.ReplyKeyboardRemove())

    ask_menu_quantity(message, class_number, campus)


# Функция для запроса количества меню
def ask_menu_quantity(message, class_number, campus):
    bot.send_message(message.chat.id, "Укажите количество порций 'завтрак школьника':")
    bot.register_next_step_handler(message, process_breakfast_quantity, class_number, campus)


# Функция для обработки ответа с количеством завтраков
def process_breakfast_quantity(message, class_number, campus):
    breakfast_quantity = message.text
    bot.send_message(message.chat.id, f"Завтрак школьника: {breakfast_quantity} порций")
    bot.send_message(message.chat.id, "Укажите количество порций 'обед школьника':")
    bot.register_next_step_handler(message, process_lunch_quantity, class_number, campus, breakfast_quantity)


# Функция для обработки ответа с количеством обедов
def process_lunch_quantity(message, class_number, campus, breakfast_quantity):
    lunch_quantity = message.text
    bot.send_message(message.chat.id, f"Обед школьника: {lunch_quantity} порции")
    bot.send_message(message.chat.id, "Укажите количество порций 'Салат':")
    bot.register_next_step_handler(message, process_salad_quantity, class_number, campus, breakfast_quantity,
                                   lunch_quantity)


# Функция для обработки ответа с количеством салатов

def process_salad_quantity(message, class_number, campus, breakfast_quantity, lunch_quantity):
    salad_quantity = message.text
    bot.send_message(message.chat.id, f"Салат: {salad_quantity} порций")
    ask_confirmation(message, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity)


# Функция для запроса подтверждения заявки
def ask_confirmation(message, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("Да", "Нет")
    bot.send_message(message.chat.id,
                     f"Корпус: {campus}\nКласс: {class_number}\n"
                     f"Завтрак школьника: {breakfast_quantity} порций\n"
                     f"Обед школьника: {lunch_quantity} порций\n"
                     f"Салат: {salad_quantity} порций\n"
                     f"Отправляем заявку?",
                     reply_markup=keyboard)
    # Используем lambda функцию для передачи user_id в обработчик
    bot.register_next_step_handler(message,
                                   lambda msg: process_order_confirmation(msg, class_number, campus, breakfast_quantity,
                                                                          lunch_quantity, salad_quantity,
                                                                          message.from_user.id))


# Функция для обработки подтверждения заявки
def process_order_confirmation(message, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity,
                               user_id):
    confirmation = message.text.lower()
    # Убираем клавиатуру после подтверждения


    if confirmation == 'да':
        # Отправляем данные в соответствующую гугл таблицу
        if campus == "1 корпус":
            bot.send_message(message.chat.id, "Ваша заявка отправлена. Спасибо!\n"
                                              "Напишите /neworder для следующей заявки",
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            send_to_google_sheet(GOOGLE_SHEET_ID_1, class_number, campus, breakfast_quantity, lunch_quantity,
                                 salad_quantity, user_id)
        else:
            bot.send_message(message.chat.id, "Ваша заявка отправлена. Спасибо!\n"
                                              "Напишите /neworder для следующей заявки",                             reply_markup=telebot.types.ReplyKeyboardRemove())
            send_to_google_sheet(GOOGLE_SHEET_ID_2, class_number, campus, breakfast_quantity, lunch_quantity,
                                 salad_quantity, user_id)
    else:
        bot.send_message(message.chat.id, "Ваша заявка не отправлена.\n Напишите /neworder, чтобы отправить заявку",
                         reply_markup=telebot.types.ReplyKeyboardRemove())


# Функция для отправки данных в гугл таблицу
def send_to_google_sheet(sheet_id, class_number, campus, breakfast_quantity, lunch_quantity,
                         salad_quantity, user_id):
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(GOOGLE_JSON_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1

        # Добавляем данные в таблицу, включая время и user_id
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = [timestamp, user_id, campus, class_number, breakfast_quantity, lunch_quantity, salad_quantity]
        sheet.append_row(row)

    except Exception as e:
        print("Error:", e)


# Запускаем бота
bot.polling()
