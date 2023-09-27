from __future__ import annotations
from loguru import logger
from typing import List, Dict
import psycopg2
from psycopg2 import extras


class ReplyFormatter:
    @staticmethod
    def fetchOne(cursor, add_keys=False) -> Dict | None:
        """
        форматирование выдачи от бд -> Dictionary | для выдачи 1 строки
        :param cursor: объект с данными от бд
        :param add_keys: boolean - формирование словаря
        :return: Dictionary
        """
        data = cursor.fetchone()

        if data is None: return data
        if not add_keys: return data

        keys = [row[0] for row in cursor.description]
        return dict(zip(keys, data))

    @staticmethod
    def fetchAll(cursor) -> List[dict] | None:
        """
        форматирование выдачи от бд -> List[ Dictionaries ] | для выдачи нескольких строк
        :param cursor: объект с данными от бд
        :return: Dictionary
        """
        keys = [row[0] for row in cursor.description]
        data = cursor.fetchall()

        if not len(data):
            return None
        else:
            return [dict(zip(keys, row)) for row in data]


class PostgresqlDb:
    """
    Обработчик для бд Postgresql
    """

    def __init__(self, host: str, port: int, name: str, username: str, password: str):
        """
        :param host: str ip addr database
        :param port: int part database
        :param name: str database name
        :param username: str login
        :param password: str password
        """
        self.host = host
        self.port = port
        self.db_name = name
        self.username = username
        self.password = password

    @logger.catch
    def exec(self, query: str, func: str = '') -> None | Dict | List[dict]:
        """
        Делает запросы в базу:

        - если тип запроса - SELECT:
        - - нужно подать тип функции собираемых данных (fetchone, fetchall)

        - если тип запроса - UPDATE, DELETE, INSERT
        - - подавать функцию не нужно

        :param query: str - query string for database
        :param func: obj - if query means select
        :return: None | dict | List[dict]
        """
        with psycopg2.connect(host=self.host,
                              port=self.port,
                              dbname=self.db_name,
                              user=self.username,
                              password=self.password,
                              sslmode='verify-full',
                              target_session_attrs='read-write') as connection:
            logger.debug("Connecting: [ok]")
            with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
                logger.debug(f"Query: [{query}] | asserted to {func}")
                cursor.execute(query)
                connection.commit()

                match func:
                    case 'fetchall':
                        reply = ReplyFormatter.fetchAll(cursor)
                        if reply is not None:
                            [logger.trace(row) for row in reply]
                        else:
                            logger.debug(f' Reply: {reply}')
                        return reply
                    case 'fetchone':
                        reply = ReplyFormatter.fetchOne(cursor, add_keys=True)
                        if reply is not None:
                            [logger.trace(row) for row in reply]
                        else:
                            logger.debug(reply)
                        return reply
                    case '':
                        return None
                    case _:
                        raise TypeError()


db = PostgresqlDb(
    host='rc1b-n347sd0msta4wqdq.mdb.yandexcloud.net',
    port=6432,
    name='bvb_shop',
    username='admin_bvb',
    password='admin_bvb',
)
