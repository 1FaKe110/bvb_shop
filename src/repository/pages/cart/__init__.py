import datetime
import json

from flask import redirect, url_for, render_template, request, Blueprint, flash
from loguru import logger
from tabulate import tabulate
from telebot.apihelper import ApiTelegramException

from assets.assets import check_session, get_next_order_id
from repository.database import db
from repository.sql import DbQueries
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
cart_page = Blueprint('cart_page', __name__)


class Cart:

    def __init__(self):
        pass

    def get_page(self, session, error_description):

        cookies = request.cookies.get('formData', None)
        logger.debug(f"{cookies = }")

        interest_products = db.exec(
            DbQueries.Products.Select.random(4),
            'fetchall'
        )
        logger.debug(interest_products)

        if error_description:
            return render_template('cart.html',
                                   products=None,
                                   order=None,
                                   clear_cookie=True,
                                   error_description=error_description,
                                   interest_products=interest_products,
                                   current_url='/cart',
                                   login=check_session(session))

        if cookies is None or len(json.loads(cookies)) < 1:
            return render_template('cart.html',
                                   products=None,
                                   order=None,
                                   clear_cookie=None,
                                   error_description=error_description,
                                   interest_products=interest_products,
                                   current_url='/cart',
                                   login=check_session(session))

        order, products = self.extend_cookies_data(cookies)

        if not check_session(session):
            return render_template('cart.html',
                                   products=products,
                                   order=order,
                                   error_description=None,
                                   clear_cookie=None,
                                   current_url='/cart',
                                   interest_products=interest_products,
                                   login=False)

        address_list = db.exec(
            DbQueries.Addresses.Select.address_by_login(session['username']),
            'fetchall')
        user_info = db.exec(
            DbQueries.Users.Select.all_by_login(session['username']),
            'fetchone')

        logger.info(f'{address_list = }')
        logger.info(f'{user_info = }')

        return render_template('cart.html',
                               products=products,
                               order=order,
                               error_description=None,
                               clear_cookie=None,
                               address_list=address_list,
                               user_info=user_info,
                               interest_products=interest_products,
                               current_url='/cart',
                               login=check_session(session))

    def add_new_order(self, session, bot):

        # получение данных с формы
        phone = request.form.get('phone') or request.form.get('phone_user')
        full_name = request.form.get('full_name') or request.form.get('full_name_user')
        order_place = request.form.get('order_place') or request.form.get('order_place_user')
        order_time = request.form.get('order_time')

        logger.debug("Проверяю наличие пользователя в бд")
        if check_session(session):
            user_id = db.exec(
                DbQueries.Users.Select.all_by_login(session['username']),
                'fetchone')
        else:
            user_id = db.exec(
                DbQueries.Users.Select.all_by_phone(phone),
                'fetchone')

        match user_id:
            case None:
                logger.debug("Пользователя нет. Добавляю нового не зарегистрированного пользователя")
                new_created_user = db.exec(
                    DbQueries.Users.Insert.new_unregistered_user(phone, full_name),
                    'fetchone'
                )

                if new_created_user.id is not None:
                    logger.debug(f"Пользователь {phone} c id: {new_created_user.id} создан")
                else:
                    logger.error(f"Ошибка создания пользователя: {phone}. Пользователю не выдан id")
                    raise RuntimeError("Не выдан id after insert в бд")

                next_order_id = get_next_order_id(db)
            case _:
                logger.debug("Пользователя найден!")
                orders_info = db.exec(
                    DbQueries.Orders.Select.by_user_id(user_id.id),
                    'fetchall'
                )
                if orders_info is None:
                    next_order_id = get_next_order_id(db)
                else:
                    for _order in orders_info:
                        is_date_valid = (datetime.datetime.fromisoformat(_order.datetime).date() ==
                                         datetime.date.today() + datetime.timedelta(days=2))
                        logger.info(f'Date valid: {is_date_valid}')
                        is_status_valid = _order.status_id == 1
                        logger.info(f'Status valid: {is_status_valid}')
                        is_address_valid = _order.address == order_place
                        logger.info(f'Address valid: {is_address_valid}')

                        if all([is_date_valid, is_status_valid, is_address_valid]):
                            next_order_id = _order.order_id
                            break
                    else:
                        next_order_id = get_next_order_id(db)
        user_address = db.exec(
                DbQueries.Addresses.Select.id_by_user_id_and_address(user_id.id, order_place),
                'fetchone'
        )
        logger.debug(f"Адрес:{order_place} пользователя id:{user_id} - {user_address}")

        if user_address is None:
            logger.debug(
                f"Для пользователя user_id: {user_id.id} не найдено адреса {order_place}. Добавляем новый адрес")
            db.exec(
                DbQueries.Addresses.Insert.new_address(user_id.id, order_place)
            )

        cookies = request.cookies.get('formData', None)
        logger.debug(f"{cookies = }")

        order, products = self.extend_cookies_data(cookies)

        logger.info(f"Полученные данные:\n"
                    f" Имя - {full_name}\n"
                    f" Телефон - {phone}\n"
                    f" Сумма заказа - {order.sum}\n"
                    f" Место доставки - {order_place}\n"
                    f" Время доставки - {order_time}\n"
                    f" Корзина:")

        logger.trace(tabulate(products))

        temp_positions = db.exec(
            DbQueries.Orders.Select.positions_by_order_id(next_order_id),
            'fetchall')

        for row in products:
            _product = db.exec(
                DbQueries.Products.Select.by_id(row.id),
                'fetchone'
            )

            new_amount = _product.amount - row.in_card
            if new_amount < 0:
                flash("Товар закончился. Приносим извинения", 'error')
                return redirect(url_for('cart'))

            db.exec(DbQueries.Products.Update.amount_by_id(row.id, new_amount))
            logger.debug(f"Обновил остаток товара с id = {row.id} в бд: ({_product.amount} -> {new_amount})")

            match temp_positions:
                case None:
                    db.exec(DbQueries.Orders.Insert.new_order(
                        next_order_id, user_id.id, row.id, _product.price, row.in_card,
                        order_place, order_time
                    ))
                case _:
                    for pos_row in temp_positions:
                        if row.id == pos_row.position_id:
                            new_amount = pos_row.amount + row.in_card
                            db.exec(DbQueries.Orders.Update.update_position_amount(
                                pos_row.id, new_amount
                            ))
                            break
                    else:
                        db.exec(DbQueries.Orders.Insert.new_order(
                            next_order_id, user_id.id, row.id, _product.price, row.in_card,
                            order_place, order_time
                        ))

        try:
            bot.__send_order__(next_order_id)
        except ApiTelegramException:
            logger.error(f"Ошибка отправки сообщения в тг. Сервис не доступен\n {ApiTelegramException}")

        return redirect(url_for('main_page.cart_clear', error_description=None))

    @staticmethod
    def extend_cookies_data(cookies):
        cart_data = json.loads(cookies)
        logger.info(f'Data from cookies: {cart_data}: {type(cart_data)}')

        products = db.exec(
            DbQueries.Products.Select.by_id_list(list(cart_data.keys())),
            'fetchall')

        logger.info(f'request type: [{request.method}] ')
        logger.info(f'products: [{json.dumps(products, indent=2, ensure_ascii=False)}] ')

        order = as_class(dict(sum=0))
        for p_row, c_row in zip(products, cart_data):
            p_row.in_card = cart_data[c_row]
            order.sum += p_row.price * p_row.in_card
        order.sum = f"{order.sum:.2f}"

        return order, products

    @staticmethod
    def clear_cookie_data(session):
        interest_products = db.exec(
            DbQueries.Products.Select.random(8),
            'fetchall'
        )

        return render_template(
            'cart.html',
            products=None,
            order=None,
            clear_cookie=True,
            interest_products=interest_products,
            current_url='/cart',
            login=check_session(session)
        )
