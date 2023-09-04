import json
from time import sleep

from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
from database import Database
from loguru import logger

RESET_DB = False
if RESET_DB:
    from database.filler import reset_database

    reset_database()

app = Flask(__name__)
app.config['UPLOADED_IMAGES_DEST'] = './static/images/all'
images = UploadSet('images', IMAGES)
configure_uploads(app, (images,))


@logger.catch
@app.route('/')
def index():
    """# Определение маршрута Flask для главной страницы"""
    # Получение списка категорий верхнего уровня
    categories = Database().execute('SELECT * FROM categories WHERE id in (1, 2)',
                                    'fetchall')
    return render_template('index.html', categories=categories)


@logger.catch
@app.route('/category/<string:category_name>')
def category(category_name):
    """# Определение маршрута Flask для путешествия по иерархии категорий"""
    # Получение выбранной категории
    cat_id = Database().execute(
        f"SELECT * FROM categories WHERE parent_id = (SELECT id FROM categories WHERE name='{category_name}')",
        'fetchone')
    prev_category = Database().execute(
        f"SELECT name FROM categories c where id = (SELECT parent_id FROM categories WHERE name = '{category_name}')",
        'fetchone')

    logger.debug(f'Проверяю наличие подкатегорий у {category_name}: [{cat_id}]')
    logger.debug(f'Родительская категория {prev_category}')

    if prev_category is None:
        prev_category = ''

    if cat_id is None:
        subcategories = None
        cookies = request.cookies.get('formData', None)
        cart_data = json.loads(cookies)
        products = Database().execute(f"SELECT * FROM products WHERE category_id in "
                                      f"(SELECT id FROM categories WHERE name='{category_name}')",
                                      'fetchall')  # Получение товаров в выбранной категории
        if len(cart_data):
            logger.debug("Продукты:")
            logger.debug(cart_data)

            for _product in products:
                if str(_product['id']) in cart_data:
                    _product['in_card'] = cart_data[str(_product['id'])]
                    logger.debug(f"id: {_product['id']} | {_product['name']}: {_product['in_card']} in card")
        else:
            pass

        return render_template('category.html',
                               prev_category=prev_category,
                               category_name=category_name,
                               category=category,
                               subcategories=subcategories,
                               products=products)

    logger.debug(f'У {category_name} есть подкатегории')
    subcategories = Database().execute(f"SELECT * FROM categories WHERE parent_id = '{cat_id['parent_id']}'",
                                       'fetchall')  # Получение дочерних категорий

    products = Database().execute(f"SELECT * FROM products WHERE category_id = '{cat_id['parent_id']}'",
                                  'fetchall')  # Получение товаров в выбранной категории

    return render_template('category.html',
                           prev_category=prev_category,
                           category_name=category_name,
                           category=category,
                           subcategories=subcategories,
                           products=products)


@logger.catch
@app.route('/product/<product_name>')
def product(product_name):
    """# Определение маршрута Flask для просмотра товара"""
    # Получение информации о товаре
    product_info = Database().execute(f"SELECT * FROM products WHERE name like '%{product_name}%'",
                                      'fetchall')[0]
    category_name = Database().execute(f"SELECT name FROM categories WHERE id = '{product_info['category_id']}'",
                                       'fetchone')['name']
    return render_template('product.html',
                           category_name=category_name,
                           product=product_info)


@logger.catch
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    """Получение данных корзины из cookies где ключом будет id товара, а значением кол-во"""
    cookies = request.cookies.get('formData', None)

    logger.debug(f"{cookies = }")

    if cookies is None or not len(cookies):
        return render_template('cart.html', products=None, order=None, clear_cookie=None)

    cart_data = json.loads(cookies)
    logger.info(f'Data from cookies: {cart_data}: {type(cart_data)}')
    products = Database().execute(f"SELECT * FROM products WHERE id in ({','.join(list(cart_data.keys()))})",
                                  'fetchall')

    logger.info(f'request type: [{request.method}] ')
    order = dict(sum=0)
    for p_row, c_row in zip(products, cart_data):
        # logger.info(c_row[str(p_row['id'])])
        p_row['in_card'] = cart_data[c_row]
        order['sum'] += p_row['price'] * p_row['in_card']
    order['sum'] = f"{order['sum']:.2f}"

    match request.method:
        case 'GET':
            return render_template('cart.html', products=products, order=order, clear_cookie=None)

        case 'POST':
            # получение данных с формы
            phone = request.form.get('phone')
            full_name = request.form.get('full_name')
            order_place = request.form.get('order_place')
            order_time = request.form.get('order_time')
            logger.info(f"Полученные данные:\n"
                        f" Имя - {full_name}\n"
                        f" Телефон - {phone}\n"
                        f" Сумма заказа - {order['sum']}\n"
                        f" Место доставки - {order_place}\n"
                        f" Время доставки - {order_time}\n"
                        f" Корзина:")
            logger.info(f'  id |   amount | name |')

            logger.debug("Проверяю наличие пользователя в бд")
            user_id = Database().execute(
                f"Select id from users where phone = '{phone}'",
                'fetchone'
            )

            if user_id is None:
                logger.debug("Пользователя нет. Добавляю нового пользователя")
                Database().execute(
                    f"INSERT into users (username, phone) values ('{full_name}', '{phone}')"
                )
                sleep(0.3)
                logger.debug('Пользователь добавлен')
                user_id = Database().execute(
                    f"Select id from users where phone = '{phone}'",
                    'fetchone'
                )

            logger.debug(f"Пользователь {phone} c {user_id}")
            user_id = user_id['id']
            last_order_id = Database().execute(
                "Select max(order_id) as last_num from orders",
                'fetchone')['last_num']

            for row in products:
                logger.info(f"{row['id']:4} | {row['in_card']:8} | {row['name']} ")

                match last_order_id:
                    case None:
                        next_order_id = 1
                    case _:
                        next_order_id = last_order_id + 1

                Database().execute(
                    'INSERT into orders (order_id, user_id, status_id, position_id, address, datetime) values'
                    f"({next_order_id}, {user_id}, 001, {row['id']}, '{order_place}', '{order_time}')",
                    'fetchone')

            return redirect(url_for('cart_clear'))


@logger.catch
@app.route('/cart/c', methods=['GET', 'POST'])
def cart_clear():
    """Метод для очистки cookie фалов"""
    return render_template('cart.html', products=None, order=None, clear_cookie=True)


@logger.catch
@app.route('/about')
def about():
    """Старинца с информацией об организации"""
    return render_template('not-ready.html')


@logger.catch
@app.route('/delivery')
def delivery():
    """Старинца с информацией о доставке"""
    return render_template('not-ready.html')


@logger.catch
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Старинца админки"""

    match request.method:
        case 'POST':
            form = request.form.to_dict()
            logger.debug(form)

            if 'ct-name' in form:
                logger.debug('Меняем что-то в категориях')
                ct_id = form.get('ct-id').replace('.', '')
                Database().execute(
                    f"UPDATE categories SET name='{form['ct-name']}', "
                    f"image_path='{'./static/images/all/' + form['сt-image_path']}' "
                    f"WHERE id={ct_id};"
                )

            if 'pr-name' in form:
                logger.debug('Меняем что-то в продуктах')
                ...

            if 'new-ct-categoryName' in form:
                logger.debug('Добавляем новую категорию')
                ...

            if 'new-pr-productName' in form:
                logger.debug('Добавляем новый продукт')
                ...

    categories = Database().execute("Select * from categories", 'fetchall')
    products = Database().execute("Select * from products", 'fetchall')

    return render_template('admin.html',
                           categories=categories,
                           products=products)


@app.route('/admin/upload', methods=['POST'])
def upload():
    if 'image' in request.files:
        filename = images.save(request.files['image'])
        logger.info(filename)
        # Обработка сохраненного файла, например, сохранение файла в базе данных или другие операции

        return redirect(url_for('admin', _method='POST'))

    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=True)
