from loguru import logger
from repository.sql import DbQueries


def get_next_order_id(db):
    last_order = db.exec(
        DbQueries.Orders.Select.last_order_id(),
        'fetchone'
    )

    match last_order.id:
        case None:
            next_order_id = 1
        case _:
            next_order_id = last_order.id + 1
    return next_order_id


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
        DbQueries.Products.Select.all_products_joined_categories_and_brands(),
        'fetchall')

    logger.debug('Добавляю индексы бд [Products] в elasticSearch')
    for record in records:
        es.index(index='products-index', id=record['p_id'], body=map_nested_dict_to_lowercase(record))

    records = db.exec(
        DbQueries.Categories.Select.all_order_by_id(),
        'fetchall')

    logger.debug('Добавляю индексы бд [Categories] в elasticSearch')
    for record in records:
        es.index(index='categories-index', id=record['c_id'], body=map_nested_dict_to_lowercase(record))
