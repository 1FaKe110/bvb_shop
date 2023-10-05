import json

import telebot
from loguru import logger
from database import db
import os


# Включаем логирование, чтобы не пропустить важные сообщения
BOT_TOKEN = os.getenv("bot_token")
CHANNEL_ID = os.getenv("channel_id")


class Telebot:
    bot = telebot.TeleBot(BOT_TOKEN)

    def send_unread_order_messages(self):
        """Декоратор для задания периодического задания"""
        logger.debug('Получаю все заказы со статусом "не прочитано"')
        unread_orders = db.exec(
            "SELECT DISTINCT (order_id) as id "
            "FROM orders "
            "WHERE status_id = 1",
            'fetchall'
        )
        for order in unread_orders:
            self.__send_order__(order['id'])

    def __send_order__(self, order_id):
        """Функция для отправки сообщения с данными заказа в указанный канал"""

        logger.debug(order_id)
        order = db.exec(
            "SELECT distinct(order_id) as id, "
            "u.phone as phone, "
            "u.username as fio, "
            "TO_CHAR(o.datetime, 'YYYY-MM-DD') as delivery_date, "
            "o.address as delivery_address "
            "FROM orders o "
            "INNER JOIN users u on u.id = o.user_id "
            f"WHERE order_id = {order_id}",
            'fetchone'
        )

        logger.debug(json.dumps(order, indent=2, ensure_ascii=False))
        message = (f"ID заказа: ``` {order['id']}```\n"
                   f"Номер телефона: ``` {order['phone']}```\n"
                   f"ФИО:``` {order['fio']} ```\n"
                   f"Позиции:\n")

        order_positions = db.exec(
            "select p.id as id, "
            "p.name as name, "
            "p.price as price, "
            "o.amount as amount, "
            "c.id as cat_id, "
            "c.name as cat_name "
            "from orders o "
            "LEFT JOIN products p on p.id = o.position_id "
            "LEFT JOIN categories c on c.id = p.category_id  "
            "WHERE TRUE "
            "and status_id = 1 "
            f"and order_id = {order['id']};",
            "fetchall"
        )
        order['positions'] = order_positions

        total_price = 0
        for pos in order['positions']:
            total_price += pos['price'] * pos['amount']
            message += (f"``` ID {pos['id']}: {pos['name']} | {pos['price']} p. | "
                        f"{pos['amount']} шт. | категория id {pos['cat_id']} - {pos['cat_name']}```\n")

        message += (f"Сумма заказа: ``` {total_price} р.```\n"
                    f"Дата доставки: ``` {order['delivery_date']}```\n"
                    f"Адрес доставки: ``` {order['delivery_address']}```\n")
        logger.debug(message)
        self.bot.send_message(chat_id=CHANNEL_ID,
                              parse_mode="Markdown",
                              text=message)


if __name__ == '__main__':
    bot = Telebot()
    bot.__send_order__(18)
