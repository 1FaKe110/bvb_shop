import json

from flask import Flask, render_template, request, make_response, redirect, url_for
from database import DbMocK as Database, test as reset_database
from loguru import logger

RESET_DB = False
if RESET_DB:
    reset_database()

app = Flask(__name__)


# Определение маршрута Flask для главной страницы
@logger.catch
@app.route('/')
def index():
    # Получение списка категорий верхнего уровня
    categories = Database().execute('SELECT * FROM categories WHERE id in (1, 2)',
                                    'fetchall')

    return render_template('index.html', categories=categories)


# Определение маршрута Flask для путешествия по иерархии категорий
@logger.catch
@app.route('/category/<string:category_name>')
def category(category_name):
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
        products = Database().execute(f"SELECT * FROM products WHERE category_id in "
                                      f"(SELECT id FROM categories WHERE name='{category_name}')",
                                      'fetchall')  # Получение товаров в выбранной категории

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


# Определение маршрута Flask для просмотра товара
@logger.catch
@app.route('/product/<product_name>')
def product(product_name):
    # Получение информации о товаре
    product_info = Database().execute(f"SELECT * FROM products WHERE name like '%{product_name}%'",
                                      'fetchall')[0]
    cat_name = Database().execute(f"SELECT name FROM categories WHERE id = '{product_info['category_id']}'",
                                  'fetchone')['name']
    return render_template('product.html',
                           category_name=cat_name,
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
            order_sum = request.form.get('order_sum')
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
            for row in products:
                logger.info(f"{row['id']:4} | {row['in_card']:8} | {row['name']} ")

            return redirect(url_for('cart_clear'))


@logger.catch
@app.route('/cart/c', methods=['GET', 'POST'])
def cart_clear():
    return render_template('cart.html', products=None, order=None, clear_cookie=True)


@logger.catch
@app.route('/about')
def about():
    return render_template('not-ready.html')


@logger.catch
@app.route('/delivery')
def delivery():
    return render_template('not-ready.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=True)
