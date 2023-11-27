import os
import json
import hashlib
import datetime
from telebot.apihelper import ApiTelegramException
from munch import DefaultMunch
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash, jsonify

from assets.assets import *
from database import db
from loguru import logger

from repository import DbQueries
from telegram_bot.Bot import Telebot
from tabulate import tabulate
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': os.getenv('elastic_host'), 'port': os.getenv('elastic_port')}])
logger.info("Connected to ElasticSearch") if es.ping() else logger.error("Could not connect to ElasticSearch")

index_postgres_data_for_search(db, es)
as_class = DefaultMunch.fromDict
app = Flask(__name__)
app.secret_key = os.getenv('secret_key')  # секретный ключ для сессий
CORS(app)
bot = Telebot()


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Обработчик для входа"""
    if request.method == 'POST':
        username = request.form['username']
        hashed_password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        logger.info(f'Хэш пароля: {hashed_password}')

        user_info = db.exec(DbQueries.Users.by_login(username), "fetchone")

        if user_info is None:
            logger.info('Пользователь не найден')
            flash('Пользователь не найден', 'error')
            return render_template('login.html')

        if user_info.password != hashed_password:
            logger.info('Не верный пароль')
            flash('Не верный логин или пароль', 'error')
            return render_template('login.html')

        session['username'] = username  # устанавливаем сессию
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Выход из личного кабинета"""
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Обработчик для регистрации"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fio = request.form['fio']
        phone = request.form['phone']
        email = request.form['email']

        # Проверка на наличие пользователя в бд по номеру телефона
        user_info = db.exec(DbQueries.Users.by_login_extended(username),
                            'fetchall')

        if user_info.is_registered:
            if user_info.email:
                flash('Пользователь с такой почтой уже существует', 'error')

            if user_info.phone:
                flash('Пользователь с таким номером телефона уже существует', 'error')

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user_info.email or user_info.phone:
            db.exec(DbQueries.Users.register_by_id(
                fio, password, email, phone, username, user_info.id
            ))

            return redirect(url_for('login'))

        db.exec(DbQueries.Users.new_user(
            username, phone, email, hashed_password, fio
        ))
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile')
def profile():
    """Страница профиля пользователя"""
    if 'username' not in session:
        return redirect(url_for('login'))

    user_info = db.exec(DbQueries.Users.by_login_extended(session['username']),
                        'fetchone')

    if user_info is None:
        return redirect(url_for('logout'))

    user_orders = db.exec(DbQueries.Orders.by_user_id(user_info.id),
                          'fetchall')

    user_addresses = db.exec(DbQueries.Addresses.by_user_id(user_info.id), 'fetchall')
    return render_template('profile.html',
                           user_info=user_info,
                           orders=user_orders,
                           addresses=user_addresses,
                           login=True)


@app.route('/profile/order/<order_id>')
def profile_order_details(order_id):
    """Страница профиля пользователя"""
    if 'username' not in session:
        return redirect(url_for('login'))

    user = db.exec(f"select id from users_new where login = '{session['username']}'", 'fetchone')
    user_order = db.exec(
        DbQueries.Orders.profile_order(order_id, user.id),
        'fetchone')

    user_order.positions = db.exec(
        DbQueries.Orders.profile_order_positions(order_id, user.id),
        'fetchall')

    order_sum = 0
    order_pos_count = 0
    for pos in user_order.positions:
        order_sum += pos.price * pos.amount
        order_pos_count += pos.amount

    user_order.positions.append(
        as_class(dict(id='Итого', price=f'{order_sum} р.', amount=order_pos_count, name='', total_amount=None))
    )

    logger.debug(json.dumps(user_order.__dict__, indent=2, ensure_ascii=False))

    return render_template('profile_order_detailed.html',
                           order=user_order,
                           login=check_session(session))


@logger.catch
@app.route('/')
def index():
    """# Определение маршрута Flask для главной страницы"""
    # Получение списка категорий верхнего уровня
    categories = db.exec(
        DbQueries.Categories.main(),
        'fetchall')

    # выбираем 4 рандомных товара из бд
    products = db.exec(
        DbQueries.Products.random(4),
        'fetchall'
    )

    return render_template('index.html',
                           categories=categories,
                           products=products,
                           login=check_session(session))


@logger.catch
@app.route('/category/<string:category_name>')
def category(category_name):
    """# Определение маршрута Flask для путешествия по иерархии категорий"""

    # Получение выбранной категории
    cat_id = db.exec(
        DbQueries.Categories.by_category(category_name),
        'fetchone')

    prev_category = db.exec(
        DbQueries.Categories.prev_category_name(category_name),
        'fetchone')

    logger.debug(f'Проверяю наличие подкатегорий у {category_name}: [{cat_id}]')
    logger.debug(f'Родительская категория {prev_category}')

    if prev_category is None:
        prev_category = ''

    if cat_id is not None:
        logger.debug(f'У {category_name} есть подкатегории')
        subcategories = db.exec(
            DbQueries.Categories.check_sub_categories(cat_id.parent_id),
            'fetchall')

        products = db.exec(f"SELECT * FROM products WHERE category_id = '{cat_id.parent_id}' ORDER BY id",
                           'fetchall')  # Получение товаров в выбранной категории

        return render_template('category.html',
                               prev_category=prev_category,
                               category_name=category_name,
                               category=category,
                               subcategories=subcategories,
                               products=products,
                               login=check_session(session))

    subcategories = None
    cookies = request.cookies.get('formData', '{}')
    cart_data = json.loads(cookies)
    products = db.exec(
        DbQueries.Products.by_category(category_name),
        'fetchall')  # Получение товаров в выбранной категории

    if products is None:
        return render_template('category.html',
                               prev_category=prev_category,
                               category_name=category_name,
                               category=category,
                               subcategories=subcategories,
                               products=products,
                               login=check_session(session))

    if not len(cart_data):
        return render_template('category.html',
                               prev_category=prev_category,
                               category_name=category_name,
                               category=category,
                               subcategories=subcategories,
                               products=products,
                               login=check_session(session))

    for _product in products:
        if str(_product.id) in cart_data:
            _product.in_card = cart_data[str(_product.id)]
            logger.debug(f"id: {_product.id} | {_product.name} | {_product.in_card} in card")

    return render_template('category.html',
                           prev_category=prev_category,
                           category_name=category_name,
                           category=category,
                           subcategories=subcategories,
                           products=products,
                           login=check_session(session))


@logger.catch
@app.route('/product/<product_name>/<product_id>')
def product(product_name, product_id):
    """# Определение маршрута Flask для просмотра товара"""

    product_info = db.exec(
        DbQueries.Products.by_name_and_id(product_name, product_id),
        'fetchone')

    category_name = db.exec(
        DbQueries.Categories.by_id(product_info.category_id),
        'fetchone')

    return render_template('product.html',
                           category_name=category_name.name,
                           product=product_info,
                           login=check_session(session))


@logger.catch
@app.route('/cart/', methods=['GET', 'POST'])
def cart(error_description=None):
    """Получение данных корзины из cookies где ключом будет id товара, а значением кол-во"""

    cookies = request.cookies.get('formData', None)
    logger.debug(f"{cookies = }")

    if error_description:
        return render_template('cart.html',
                               products=None,
                               order=None,
                               clear_cookie=True,
                               error_description=error_description,
                               login=check_session(session))

    if cookies is None or len(json.loads(cookies)) < 1:
        return render_template('cart.html',
                               products=None,
                               order=None,
                               clear_cookie=None,
                               login=check_session(session))

    cart_data = json.loads(cookies)
    logger.info(f'Data from cookies: {cart_data}: {type(cart_data)}')
    products = db.exec(
        DbQueries.Products.by_id_list(list(cart_data.keys())),
        'fetchall')

    logger.info(f'request type: [{request.method}] ')
    logger.info(f'products: [{json.dumps(products, indent=2, ensure_ascii=False)}] ')
    order = as_class(dict(sum=0))
    for p_row, c_row in zip(products, cart_data):
        p_row.in_card = cart_data[c_row]
        order.sum += p_row.price * p_row.in_card
    order.sum = f"{order.sum:.2f}"

    match request.method:
        case 'GET':
            if check_session(session):
                address_list = db.exec(
                    DbQueries.Addresses.by_login(session['username']),
                    'fetchall')
                user_info = db.exec(
                    DbQueries.Users.by_login_extended(session['username']),
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
                                       login=check_session(session))

            return render_template('cart.html',
                                   products=products,
                                   order=order,
                                   error_description=None,
                                   clear_cookie=None,
                                   login=check_session(session))

        case 'POST':
            # получение данных с формы
            phone = request.form.get('phone') or request.form.get('phone_user')
            full_name = request.form.get('full_name') or request.form.get('full_name_user')
            order_place = request.form.get('order_place') or request.form.get('order_place_user')
            order_time = request.form.get('order_time')

            logger.debug("Проверяю наличие пользователя в бд")
            if check_session(session):
                user_id = db.exec(
                    DbQueries.Users.by_login_extended(session['username']),
                    'fetchone')
            else:
                user_id = db.exec(
                    DbQueries.Users.by_phone(phone),
                    'fetchone')

            match user_id:
                case None:
                    user_id = add_new_user(full_name, phone, db)
                    next_order_id = get_next_order_id(db)
                case _:
                    logger.debug("Пользователя найден!")
                    orders_info = db.exec(DbQueries.Orders.by_user_id(user_id.id),
                                          'fetchall')
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

            check_user_address(order_place, user_id.id, db)

            logger.info(f"Полученные данные:\n"
                        f" Имя - {full_name}\n"
                        f" Телефон - {phone}\n"
                        f" Сумма заказа - {order.sum}\n"
                        f" Место доставки - {order_place}\n"
                        f" Время доставки - {order_time}\n"
                        f" Корзина:")

            logger.trace(tabulate(products))

            temp_positions = db.exec(
                DbQueries.Orders.positions_by_order_id(next_order_id),
                'fetchall')

            for row in products:
                _product = db.exec(
                    DbQueries.Products.by_id(row.id),
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

            return redirect(url_for('cart_clear', error_description=None))


# Маршрут для выполнения поисковых запросов
@app.route('/search', methods=['GET'])
def search():
    user_request = request.args.get('q')
    if not user_request:
        return jsonify(dict(code='error', message='Missing search term'))

    # Поиск в ElasticSearch продуктов
    res = es.search(index="products-index",
                    body={"query": {
                        "match": {
                            "p_name": {
                                "query": user_request,
                                "boost": 1.0,
                                "fuzziness": "2"
                            }}}})
    products = [row['_source'] for row in res['hits']['hits']]

    # Поиск в ElasticSearch категорий
    res = es.search(index="categories-index",
                    body={"query": {
                        "match": {
                            "c_name": {
                                "query": user_request,
                                "boost": 1.0,
                                "fuzziness": "2"
                            }}}})
    categories = [row['_source'] for row in res['hits']['hits']]

    logger.info("Результаты запроса в бд [Products]")
    logger.info(json.dumps(products, indent=2, ensure_ascii=False))

    logger.info("Результаты запроса в бд [Categories]")
    logger.info(json.dumps(categories, indent=2, ensure_ascii=False))

    return render_template('search.html',
                           products=products,
                           categories=categories,
                           user_request=user_request,
                           session=check_session(session))


@app.route('/search-helper', methods=['GET'])
def search_helper():
    """ Подсказки для поисковой строки """

    user_request = request.args.get('q')

    # Поиск в ElasticSearch категорий
    res = es.search(index="categories-index",
                    body={"query": {
                        "match": {
                            "c_name": {
                                "query": user_request,
                                "boost": 1.0,
                                "fuzziness": "1"
                            }}}})
    categories = [row['_source'] for row in res['hits']['hits']][:5]
    return jsonify(categories)

@logger.catch
@app.route('/cart/c/', methods=['GET', 'POST'])
def cart_clear():
    """Метод для очистки cookie фалов"""

    return render_template('cart.html',
                           products=None,
                           order=None,
                           clear_cookie=True,
                           login=check_session(session))


@logger.catch
@app.route('/about')
def about():
    """Старинца с информацией об организации"""
    return render_template('about_us.html', login=check_session(session))


@logger.catch
@app.route('/delivery')
def delivery():
    """Старинца с информацией о доставке"""
    return render_template('delivery.html', login=check_session(session))


@app.errorhandler(404)
def page_not_found(error):
    """Страница 'страница не найдена'"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_page(error):
    """Страница 'страница не найдена'"""
    return render_template('500.html'), 500


@app.route('/error_500')
def nonexistent_page():
    """Пример эндпоинта, которого нет"""
    # Генерируем ошибку 404 "Страница не найдена"
    abort(500)


def main():
    app.run(host='0.0.0.0', port=1111, debug=True)


if __name__ == '__main__':
    main()
