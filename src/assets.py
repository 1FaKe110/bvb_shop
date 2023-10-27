from loguru import logger
from time import sleep


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
                      'fetchone').id
    logger.debug(f"Пользователь {phone} c {user_id}")
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
