import requests
import xml.etree.ElementTree as ET
from loguru import logger
from database import Database


class Tasks:

    @staticmethod
    def update_dollar_course():
        # Выполните запрос к API для получения курса доллара к рублю
        logger.debug("Запрашиваю курс доллара у ЦБ")
        response = requests.get('https://www.cbr.ru/scripts/XML_daily.asp')
        logger.trace(response)
        usd_rate = float(
            ET.fromstring(response.text)
            .find("./Valute[CharCode='USD']/Value")
            .text.replace(",", "."))
        logger.debug(f"Курс Доллара: {usd_rate} рублей. Обновляю данные в бд")

        Database().execute(
            f'UPDATE dollar SET price={usd_rate} WHERE id=1;'
        )
        products_in_dollars = Database().execute(
            "Select id, by_price, price_dependency "
            "from products ",
            "fetchall"
        )
        logger.debug('Обновляю цены товаров')
        for product in products_in_dollars:
            if product['price_dependency']:
                price = round(product['by_price'] * 1.5 * usd_rate, 0)
            else:
                price = round(product['by_price'] * 1.5, 0)

            Database().execute(
                f'UPDATE products SET price={price} WHERE id={product["id"]};'
            )

        # Обновите значение в таблице или базе данных
        # Например, для обновления значения в базе данных, вам может понадобиться ORM или SQL-запрос
        ...


def main():
    Tasks.update_dollar_course()


if __name__ == '__main__':
    main()
