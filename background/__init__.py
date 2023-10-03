import datetime

import requests
import xml.etree.ElementTree as ET
from loguru import logger
from database import db

from munch import DefaultMunch
as_class = DefaultMunch.fromDict


class Tasks:

    @staticmethod
    def update_dollar_course():
        # Выполните запрос к API для получения курса доллара к рублю
        dollar = db.exec('select * from dollar', 'fetchone')

        update_delta = datetime.datetime.now() - dollar.last_update
        if update_delta.total_seconds() <= 3600:
            return

        logger.debug("Запрашиваю курс доллара у ЦБ")
        response = requests.get('https://www.cbr.ru/scripts/XML_daily.asp')
        logger.trace(response)
        usd_rate = float(
            ET.fromstring(response.text)
            .find("./Valute[CharCode='USD']/Value")
            .text.replace(",", "."))
        logger.debug(f"Курс Доллара: {usd_rate} рублей. Обновляю данные в бд")

        db.exec(f"UPDATE dollar SET "
                f"price={usd_rate}, "
                f"last_update='{datetime.datetime.now().isoformat()}' "
                f"WHERE id=1;")

        products = db.exec(
            "Select id, by_price, price_dependency "
            "from products ",
            "fetchall"
        )
        logger.debug('Обновляю цены товаров')
        for product in products:
            if product.price_dependency:
                price = round(product.by_price * 1.5 * usd_rate, 0)
            else:
                price = round(product.by_price * 1.5, 0)

            db.exec(
                f'UPDATE products SET price={price} WHERE id={product.id};'
            )


def main():
    Tasks.update_dollar_course()


if __name__ == '__main__':
    main()
