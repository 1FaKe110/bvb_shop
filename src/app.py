import os
import json
import hashlib
import datetime
from telebot.apihelper import ApiTelegramException
from munch import DefaultMunch
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash, make_response

from assets import *
from database import db
from loguru import logger
from telegram_bot.Bot import Telebot
from tabulate import tabulate

as_class = DefaultMunch.fromDict
app = Flask(__name__)
app.secret_key = os.getenv('secret_key')  # секретный ключ для сессий
CORS(app)
bot = Telebot()


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Обработчик для входа"""
    if request.method == 'POST':
        _login = request.form['username']
        hashed_password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        logger.info(f'Хэш пароля: {hashed_password}')

        user_info = db.exec(f"Select login, password "
                            f"from users_new "
                            f"where login = '{_login}'", "fetchone")

        if user_info is None:
            logger.info('Пользователь не найден')
            flash('Пользователь не найден', 'error')
            return render_template('login.html')

        if user_info.password != hashed_password:
            logger.info('Не верный пароль')
            flash('Не верный логин или пароль', 'error')
            return render_template('login.html')

        session['username'] = _login  # устанавливаем сессию
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
        user_info = db.exec(f"SELECT phone FROM users WHERE login = '{username}'", 'fetchall')
        if user_info:
            flash('Пользователь с таким номером телефона уже существует', 'error')

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db.exec("INSERT INTO users_new "
                "(login, phone, email, password, is_registered, fio) "
                "VALUES "
                f"('{username}', '{phone}', '{email}', '{hashed_password}', true, '{fio}');")

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile')
def profile():
    """Страница профиля пользователя"""
    if 'username' not in session:
        return redirect(url_for('login'))

    user_info = db.exec(f"select id, fio, login, phone, email from users_new where login = '{session['username']}'",
                        'fetchone')
    user_orders = db.exec(f"select distinct(o.order_id), o.address, cast(datetime as text), os.name from orders o "
                          f"inner join order_status os on os.id = o.status_id "
                          f"where user_id = {user_info.id}",
                          'fetchall')
    user_addresses = db.exec(f"select * from addresses where user_id = {user_info.id}", 'fetchall')
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
    user_order = db.exec(f"select distinct(o.order_id), "
                         f"o.status_id, "
                         f"os.name as status_name, "
                         f"o.address, "
                         f"cast(cast(o.datetime as date) as text), "
                         f"cast(o.creation_time as text) "
                         f"from orders o "
                         f"inner join order_status os on os.id = o.status_id "
                         f"where true "
                         f"and order_id = {order_id} "
                         f"and user_id = {user.id}", 'fetchone')

    user_order.positions = db.exec(f"select o.position_id as id, "
                                   f"o.position_price as price, "
                                   f"o.amount, "
                                   f"p.amount as total_amount, "
                                   f"p.name "
                                   f"from orders o "
                                   f"inner join products p on p.id = o.position_id "
                                   f"where true "
                                   f"and order_id = {order_id} "
                                   f"and user_id = {user.id}", 'fetchall')

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
    categories = db.exec('SELECT * FROM categories WHERE parent_id is Null ORDER BY id',
                         'fetchall')
    return render_template('index.html',
                           categories=categories,
                           login=check_session(session))


@logger.catch
@app.route('/category/<string:category_name>')
def category(category_name):
    """# Определение маршрута Flask для путешествия по иерархии категорий"""

    # Получение выбранной категории
    cat_id = db.exec(
        f"SELECT * FROM categories "
        f"WHERE parent_id = (SELECT id FROM categories WHERE name='{category_name}') ORDER BY id",
        'fetchone')
    prev_category = db.exec(
        f"SELECT name FROM categories c "
        f"where id = (SELECT parent_id FROM categories WHERE name = '{category_name}')  ORDER BY id",
        'fetchone')

    logger.debug(f'Проверяю наличие подкатегорий у {category_name}: [{cat_id}]')
    logger.debug(f'Родительская категория {prev_category}')

    if prev_category is None:
        prev_category = ''

    if cat_id is not None:
        logger.debug(f'У {category_name} есть подкатегории')
        subcategories = db.exec(f"SELECT * FROM categories WHERE parent_id = '{cat_id.parent_id}'  ORDER BY id",
                                'fetchall')  # Получение дочерних категорий

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
    cookies = request.cookies.get('formData', None)
    cart_data = json.loads(cookies)
    products = db.exec(f"SELECT * FROM products WHERE category_id in "
                       f"(SELECT id FROM categories WHERE name='{category_name}') "
                       f"ORDER BY id",
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

    product_info = db.exec(fr"SELECT * FROM products WHERE name = '{product_name}' and id = {product_id}",
                           'fetchall')[0]
    category_name = db.exec(f"SELECT name FROM categories WHERE id = '{product_info['category_id']}'",
                            'fetchone').name
    return render_template('product.html',
                           category_name=category_name,
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
    products = db.exec(f"SELECT * FROM products "
                       f"WHERE id in ({','.join(list(cart_data.keys()))}) "
                       f"order by id asc",
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
                address_list = db.exec("select address "
                                       "from addresses a "
                                       "inner join users_new un on un.id = a.user_id  "
                                       f"where un.login = '{session['username']}'",
                                       'fetchall')
                user_info = db.exec('SELECT phone, fio '
                                    'FROM users_new un '
                                    f"where un.login = '{session['username']}'",
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
            phone = request.form.get('phone')
            full_name = request.form.get('full_name')
            order_place = request.form.get('order_place')
            order_time = request.form.get('order_time')

            logger.debug("Проверяю наличие пользователя в бд")
            user_id = db.exec(f"Select id from users_new "
                              f"where phone = '{phone}'",
                              'fetchone')

            if user_id is None:
                user_id = add_new_user(full_name, phone, db)
                next_order_id = get_next_order_id(db)
            else:
                logger.debug("Пользователя найден!")
                orders_info = db.exec("select distinct(order_id), "
                                      "address, creation_time, status_id "
                                      "from orders "
                                      f"where user_id = {user_id.id}",
                                      'fetchall')
                if orders_info is not None:
                    for _order in orders_info:
                        is_date_valid = _order.creation_time.date() == datetime.date.today()
                        is_status_valid = _order.status_id == 1
                        is_address_valid = _order.address == order_place

                        if all([is_date_valid, is_status_valid, is_address_valid]):
                            next_order_id = _order.order_id
                            break
                    else:
                        next_order_id = get_next_order_id(db)
                else:
                    next_order_id = get_next_order_id(db)

            check_user_address(order_place, user_id, db)

            logger.info(f"Полученные данные:\n"
                        f" Имя - {full_name}\n"
                        f" Телефон - {phone}\n"
                        f" Сумма заказа - {order.sum}\n"
                        f" Место доставки - {order_place}\n"
                        f" Время доставки - {order_time}\n"
                        f" Корзина:")

            logger.info(tabulate(products))
            for row in products:
                _product = db.exec(
                    f"select amount, price from products where id={row.id}",
                    'fetchone'
                )

                new_amount = _product.amount - row.in_card
                if new_amount < 0:
                    flash("Товар закончился. Приносим извинения", 'error')

                db.exec('INSERT into orders '
                        '(order_id, user_id, status_id, position_id, '
                        'position_price, amount, address, datetime, creation_time) '
                        'values '
                        f"({next_order_id}, {user_id.id}, 001, {row.id}, {_product.price}, {row.in_card}, "
                        f"'{order_place}', '{order_time}', '{datetime.datetime.now().isoformat()}')"
                        )

                db.exec(f"UPDATE products SET amount={new_amount} WHERE id={row.id};")
                logger.debug(f"Обновил остаток товара с id = {row.id} в бд: ({_product.amount} -> {new_amount})")

            try:
                bot.__send_order__(next_order_id)
            except ApiTelegramException:
                logger.error(f"Ошибка отправки сообщения в тг. Сервис не доступен\n {ApiTelegramException}")

            return redirect(url_for('cart_clear', error_description=None))


@app.route('/search', methods=['POST'])
def search():
    # Получение данных из формы
    query = request.form['query']
    _products = db.exec(f"SELECT * FROM products "
                        f"WHERE true "
                        f"and name LIKE '%{query}%' "
                        f"and amount > 0 "
                        f"order by category_id asc;", 'fetchall')
    _categories = db.exec(f"SELECT * FROM categories "
                          f"WHERE true "
                          f"and name LIKE '%{query}%' "
                          f"", 'fetchall')
    return render_template('not_ready.html', login=check_session(session))


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
