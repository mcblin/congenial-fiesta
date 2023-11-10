# Telegram bot for school canteen requests

Этот проект представляет собой телеграм-бота, который позволяет пользователям делать заявки на обед в школу. Бот спрашивает номер класса, выбор корпуса, количество порций завтрака и обеда. Заявки отправляются в Google Таблицу для дальнейшей обработки.

## Требования

Для работы этого проекта, вам понадобятся:

- Python 3.6 и выше;
- Библиотека `pyTelegramBotAPI`;
- Библиотека `gspread` для работы с Google Таблицами;
- Библиотека `datetime`;
- Учетные данные сервисного аккаунта Google (JSON-файл).

## Установка

1. Установите зависимости, запустив следующую команду: `pip install pyTelegramBotAPI gspread google-auth`


2. Зарегистрируйте нового бота у [BotFather](https://t.me/BotFather) в Telegram и получите токен для вашего бота.

3. Создайте Google Таблицы для хранения заявок на обед в каждом из корпусов. Получите Google Sheet ID для каждой таблицы.

4. Получите учетные данные сервисного аккаунта Google (JSON-файл) и разрешите доступ к таблицам, которые вы создали.

5. Вставьте токен бота, Google Sheet IDs и путь к JSON-файлу с учетными данными Google в соответствующие переменные в коде телеграм-бота.
   
```python
# Замените следующие строки своими данными
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
GOOGLE_JSON_FILE = 'path/to/your/google-credentials.json'
GOOGLE_SHEET_ID_1 = 'YOUR_GOOGLE_SHEET_ID_FOR_CAMPUS_1'
GOOGLE_SHEET_ID_2 = 'YOUR_GOOGLE_SHEET_ID_FOR_CAMPUS_2' 
```

## Запуск

Запустите телеграм-бота, выполнив следующую команду в терминале, где находится ваш проект:

`python your_telegram_bot.py`

*Замените your_telegram_bot.py на имя вашего Python-файла с кодом телеграм-бота. В остальном, следуйте инструкциям и описанию вашего проекта.*

## Другие меню

Вы можете легко добавить новые меню в бота "Школьные обеды", следуя указаниям ниже:

1. В файле `your_telegram_bot.py` добавьте новые функции для обработки запроса количества выбранного блюда и его подтверждения, аналогично уже существующим функциям для других блюд. Назовите эти функции соответственно (например, `process_salad_quantity`).
2. В функции `process_lunch_quantity`, после обработки количества обедов "Обед школьника", вызовите функцию для запроса количества выбранного нового блюда. Например:
  ```python
 def process_lunch_quantity(message, class_number, campus, breakfast_quantity):
    lunch_quantity = message.text
    bot.send_message(message.chat.id, f"Обед школьника: {lunch_quantity} порций")
    bot.send_message(message.chat.id, "Укажите количество порций салата:")
    bot.register_next_step_handler(message, process_salad_quantity, class_number, campus, breakfast_quantity, lunch_quantity)
```
4. В функции `process_salad_quantity` вызываем функцию `ask_confirmation` и добавляем туда количество порций салата. Примерно так выглядит функция:
```python
def process_salad_quantity(message, class_number, campus, breakfast_quantity, lunch_quantity):
    salad_quantity = message.text
    bot.send_message(message.chat.id, f"Салат: {salad_quantity} порций")
    ask_confirmation(message, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity)
```

5. В функции `ask_confirmation`, добавьте новое поле для отображения количества выбранного нового блюда в сообщении с подтверждением заявки. Например:
   
```python
def ask_confirmation(message, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("Да", "Нет")
    bot.send_message(message.chat.id,
                     f"Корпус: {campus}\nКласс: {class_number}\n"
                     f"Завтрак школьника: {breakfast_quantity} порций\n"
                     f"Обед школьника: {lunch_quantity} порций\n"
                     f"Новое меню: {new_menu_quantity} порций\n"
                     f"Отправляем заявку?",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, process_order_confirmation, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity)
```
6. В функции `process_order_confirmation`, добавьте новый параметр для количества нового блюда в вызов функции `send_to_google_sheet` для отправки данных в гугл таблицу. Например:
```python
def process_order_confirmation(message, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity):
    ...
    if confirmation == 'да':
        # Отправляем данные в соответствующую гугл таблицу
        if campus == "1 корпус":
            send_to_google_sheet(GOOGLE_SHEET_ID_1, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity)
        else:
            send_to_google_sheet(GOOGLE_SHEET_ID_2, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity)
```
7. В функции `send_to_google_sheet`, добавьте новое поле с количеством нового блюда в список row, чтобы данные о нем отправлялись в гугл таблицу. Например:
   ```python
   def send_to_google_sheet(sheet_id, class_number, campus, breakfast_quantity, lunch_quantity, salad_quantity):
    try:
        # ... (предыдущий код)
        # Добавляем данные в таблицу
        row = [campus, class_number, breakfast_quantity, lunch_quantity, salad_quantity]
        sheet.append_row(row)
    except Exception as e:
        print("Error:", e)
   ```
   
8. В Google Таблицах:
   - Убедитесь, что у вас есть соответствующие таблицы с правильными заголовками для новых меню. Вы можете добавить новые столбцы для каждого нового меню и указать их в коде функции `send_to_google_sheet`.


## Как пользоваться

1. Напишите `/start` или `/neworder` для начала взаимодействия с ботом.

2. Бот попросит вас ввести номер класса (например, 2Б).

3. Затем бот предложит выбрать корпус (например, 1 корпус или 2 корпус).

4. Далее, бот запросит выбрать одно из доступных меню, например:
        - Завтрак школьника
        - Обед мясной
        - Обед вегетарианский
        - Другое меню
5. После того, как вы введете все данные, бот попросит подтвердить заявку.

6. Если вы подтвердите заявку, данные будут отправлены в соответствующую Google Таблицу.

7. Если вы не являетесь авторизованным пользователем, бот не позволит вам создавать заявки.

## Лицензия

Этот проект лицензирован под [Apache License 2.0](LICENSE).
