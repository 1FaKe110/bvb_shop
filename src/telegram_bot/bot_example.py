import telebot
import schedule
import time
from src.database import Database
from loguru import logger

# Создание экземпляра бота с указанным токеном
BOT_TOKEN = '6542986021:AAGhL8Yf4bTLdI5cf48Pf6ryksmaFJW6-7c'
CHANNEL_ID = '-1001845833328'

bot = telebot.TeleBot(BOT_TOKEN)


def send_unread_order_messages():
    """Декоратор для задания периодического задания"""

    # Здесь должна быть логика для получения заказов в статусе "не прочитано" из базы данных
    logger.debug('Получаю все заказы со статусом "не прочитано"')
    unread_orders = Database().execute(
        'select * from orders where status_id = 1',
        'fetchall'
    )
    for order in unread_orders:
        send_order_message(order)


#
def send_order_message(order):
    """Функция для отправки сообщения с данными заказа в указанный канал"""

    message = f"""
    ID заказа: {order['id']}
    Номер телефона: {order['phone']}
    ФИО: {order['fio']}
    Сумма заказа: {order['price']}
    Состав заказа: {order['composition']}
    Дата доставки: {order['delivery_date']}
    Адрес доставки: {order['delivery_address']}
    """
    bot.send_message(chat_id=CHANNEL_ID,
                     text=message)


@bot.message_handler(func=lambda message: True)
def handle_status_updates(message):
    """Функция для обработки ответов пользователя и изменения статуса заказа"""
    chat_id = message.chat.id
    message_text = message.text.lower()
    status_code = None

    if message_text == "не прочитано":
        status_code = "1"
    elif message_text == "на выполнении":
        status_code = "2"
    elif message_text == "выполнено":
        status_code = "3"
    elif message_text == "отменено":
        status_code = "4"
    elif message_text == "возобновлено":
        status_code = "5"

    if status_code:
        # Обработка изменения статуса заказа
        order_id = ...  # Предполагается, что есть способ получить ID заказа
        update_order_status(order_id, status_code)
        bot.send_message(chat_id, f"Статус заказа {order_id} изменен на {message_text}")


def update_order_status(order_id, status_code):
    """Функция для изменения статуса заказа и обработки товаров"""
    # Здесь должна быть логика для изменения статуса заказа в базе данных

    # Обработка заказа при статусе "отменено"
    if status_code == "401":
        decrease_product_amounts(order_id)

    # Обработка заказа при статусе "возобновлено"
    elif status_code == "301":
        increase_product_amounts(order_id)


def decrease_product_amounts(order_id):
    """Функция для уменьшения количества товаров в БД при отмене заказа"""
    # Здесь должна быть логика для уменьшения количества товаров в базе данных
    pass


def increase_product_amounts(order_id):
    """Функция для увеличения количества товаров в БД при возобновлении заказа"""
    # Здесь должна быть логика для увеличения количества товаров в базе данных
    pass


def run_scheduler():
    """Запуск планировщика заданий"""
    # Периодическая отправка сообщений о заказах в статусе "не прочитано"
    schedule.every(3).hours.do(send_unread_order_messages)
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    run_scheduler()
    bot.send_message(CHANNEL_ID, '1234')
    bot.polling(none_stop=True)
    order = {
        'id': 134,
        'phone': '+79774986485',
        'fio': "тут был кто-то",
        'total_price': '300',
        'composition': [
            {'name': 'Кран 1', "amount": 10, 'sell_price': 10},
            {'name': 'Кран 2', "amount": 20, 'sell_price': 10}
        ],
        'delivery_date': '2023-08-23',
        'delivery_address': 'а я хз где я живу'
    }

    send_order_message(order)


# Запуск бота и планировщика заданий
if __name__ == "__main__":
    main()
