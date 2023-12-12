from loguru import logger
from time import sleep

from repository.sql import DbQueries


def get_next_order_id(db):
    last_order_id = db.exec("Select max(order_id) as last_num from orders",
                            'fetchone').last_num
    match last_order_id:
        case None:
            next_order_id = 1
        case _:
            next_order_id = last_order_id + 1
    return next_order_id


def add_new_user(full_name, phone, db):
    logger.debug("Пользователя нет. Добавляю нового пользователя")
    db.exec(f"INSERT into users_new (fio, phone) values ('{full_name}', '{phone}')")
    sleep(0.3)
    logger.debug('Пользователь добавлен')
    user_id = db.exec(f"Select id from users_new "
                      f"where phone = '{phone}' and "
                      f"fio = '{full_name}'",
                      'fetchone')
    logger.debug(f"Пользователь {phone} c {user_id.id}")
    return user_id


def check_user_address(order_place, user_id, db):
    # Проверка наличия этого адреса у пользователя
    if db.exec("select * from public.addresses "
               "where true "
               f"and user_id = {user_id} "
               f"and address = '{order_place}'", 'fetchone') is None:
        db.exec(f"INSERT INTO public.addresses "
                f"(user_id, address) "
                f"VALUES ({user_id}, '{order_place}');")


def check_session(session):
    return True if 'username' in session else False


def map_nested_dict_to_lowercase(d):
    for key, value in d.items():
        if isinstance(value, str):
            d[key] = value.lower()
        elif isinstance(value, dict):
            map_nested_dict_to_lowercase(value)
    return d


def index_postgres_data_for_search(db, es):
    records = db.exec(
        DbQueries.Products.all(),
        'fetchall')

    logger.debug('Добавляю индексы бд [Products] в elasticSearch')
    for record in records:
        es.index(index='products-index', id=record['p_id'], body=map_nested_dict_to_lowercase(record))

    records = db.exec(
        DbQueries.Categories.all(),
        'fetchall')

    logger.debug('Добавляю индексы бд [Categories] в elasticSearch')
    for record in records:
        es.index(index='categories-index', id=record['c_id'], body=map_nested_dict_to_lowercase(record))
