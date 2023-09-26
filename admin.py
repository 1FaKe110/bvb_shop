import json

import flask
from flask import Flask, render_template, request, redirect, url_for, abort
from database import Database
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from background import Tasks

Tasks.update_dollar_course()
app = Flask(__name__)


@logger.catch
@app.route('/')
def index():
    return redirect(url_for('categories'))


@logger.catch
@app.route('/categories', methods=['GET', 'POST'])
def categories():
    match request.method:
        case 'POST':
            form = request.form.to_dict()
            logger.debug(form)

            logger.debug('Меняем что-то в категориях')
            ct_id = form.get('ct-id').replace('.', '')
            ct_name = form.get('ct-name')
            ct_image_path = form.get('categoryImagePath', 'Null')
            Database().execute(
                f"UPDATE categories SET name='{ct_name}', image_path='{ct_image_path}' WHERE id={ct_id};"
            )

    categories_list = Database().execute("Select * from categories", 'fetchall')
    return render_template('admin_categories.html',
                           categories=categories_list)


@app.route('/categories/delete/<category_id>')
def product_delete(category_id):
    """Delete product from database"""
    logger.debug(f"Removing categories with id: {category_id}")
    try:
        Database().execute(f"DELETE FROM categories WHERE id={category_id};")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/products', methods=['GET', 'POST'])
def products():
    match request.method:
        case 'POST':
            form = request.form.to_dict()
            logger.debug(form)

            logger.debug('Меняем что-то в продуктах')
            pr_id = form.get('pr-id')

            Database().execute(
                f"UPDATE products SET "
                f"name='{form['pr-name']}', "
                f"by_price={form['pr-by_price']}, "
                f"price={form['pr-price']}, "
                f"amount={form['pr-amount']}, "
                f"brand='{form['pr-brand']}', "
                f"price_dependency={form['pr-price_dependency']}, "
                f"category_id={form['categoryParentName']}, "
                f"image_id=Null, "
                f"description='{form['pr-description']}', "
                f"image_path='{form.get('categoryImagePath', '../../static/images/products/products-blank.png')}' "
                f"WHERE id={pr_id}; "
            )

    dollar = Database().execute("Select * from dollar where id = 1", 'fetchone')
    products_list = Database().execute("Select * from products", 'fetchall')
    categories_list = Database().execute("Select * from categories", 'fetchall')
    return render_template('admin_products.html',
                           categories=categories_list,
                           products=products_list,
                           dollar=dollar)


@app.route('/products/delete/<product_id>')
def category_delete(product_id):
    """Delete product from database"""
    logger.debug(f"Removing product with id: {product_id}")
    try:
        Database().execute(f"DELETE FROM products WHERE id={product_id};")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    match request.method:
        case 'POST':
            form = request.form.to_dict()
            logger.debug(json.dumps(form, indent=2, ensure_ascii=False))
            logger.debug('Меняем что-то в заказах')

    orders_list = Database().execute(
        "Select distinct(order_id), user_id, status_id, address, datetime, ose.id as status_id, ose.name "
        "from orders o "
        "inner join order_status_enum ose on ose.id = o.status_id ",
        'fetchall')
    for _order in orders_list:
        _order['sum'] = 0
        _order['positions'] = Database().execute(
            "select p.id as id, "
            "p.name as name, "
            "p.price as price, "
            "o.amount as amount "
            "from orders o "
            "LEFT JOIN products p on p.id = o.position_id "
            "WHERE TRUE "
            f"and order_id = {_order['order_id']};",
            "fetchall"
        )
        for position in _order['positions']:
            _order['sum'] += position['price'] * position['amount']

    order_statuses = Database().execute("Select * from order_status_enum", 'fetchall')
    return render_template('admin_orders.html',
                           orders=orders_list,
                           order_statuses=order_statuses)


@logger.catch
@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order(order_id):
    match request.method:
        case 'POST':
            form = request.form.to_dict()
            logger.debug(json.dumps(form, indent=2, ensure_ascii=False))
            logger.debug('Меняем что-то в заказах')

    orders_list = Database().execute(
        "Select distinct(order_id), status_id, address, datetime, ose.id as status_id, ose.name as status_name, u.username, u.phone, u.email "
        "from orders o "
        "inner join order_status_enum ose on ose.id = o.status_id "
        "inner join users u on o.user_id = u.id "
        f"where order_id = {order_id}",
        'fetchall')

    if not len(orders_list):
        return redirect(url_for('orders'))

    for _order in orders_list:
        _order['sum'] = 0
        _order['positions'] = Database().execute(
            "select p.id as id, "
            "p.name as name, "
            "p.price as price, "
            "o.amount as amount "
            "from orders o "
            "LEFT JOIN products p on p.id = o.position_id "
            "WHERE TRUE "
            f"and order_id = {order_id};",
            "fetchall"
        )
        for position in _order['positions']:
            _order['sum'] += position['price'] * position['amount']

    logger.debug(json.dumps(orders_list, indent=2, ensure_ascii=False))
    order_statuses = Database().execute("Select * from order_status_enum", 'fetchall')
    return render_template('admin_order_detailed.html',
                           order=orders_list[0],
                           order_statuses=order_statuses)


@app.route('/order/<order_id>/delete', methods=['DELETE'])
def order_delete(order_id):
    """Delete order from database"""
    logger.debug(f"Removing order with id: {order_id}")

    try:
        Database().execute(f"UPDATE orders SET status_id=4 WHERE order_id={order_id};")
        item_list = Database().execute(f"SELECT o.position_id as opid, o.amount as oam, p.amount as pam "
                                       "from orders o "
                                       "inner join products p on p.id = o.position_id "
                                       f"where order_id={order_id};")
        for item in item_list:
            total_price = item['oam'] + item['pam']
            Database().execute(f"UPDATE products SET amount={total_price} WHERE id={item['opid']};")

        logger.debug("вернул товары из удаленного заказа на полки")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@app.route('/order/<order_id>/update', methods=['POST'])
def order_update(order_id):
    """update order in database"""
    logger.debug(f"updating order with id: {order_id}")

    data = request.json

    Database().execute()

    try:
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/order/<order_id>/delete/<item_id>', methods=['DELETE'])
def order_delete_item(order_id, item_id):
    """Delete order from database"""
    logger.debug(f"Removing item #{item_id} from order_id #{order_id}")
    try:
        item_list = Database().execute(f"SELECT o.position_id as opid, o.amount as oam, p.amount as pam "
                                       "from orders o "
                                       "inner join products p on p.id = o.position_id "
                                       f"where o.order_id={order_id} and o.position_id={item_id};",
                                       'fetchall')
        Database().execute(f"DELETE FROM orders WHERE order_id={order_id} and position_id={item_id};")
        for item in item_list:
            total_amount = item['oam'] + item['pam']
            Database().execute(f"UPDATE products SET amount={total_amount} WHERE id={item['opid']};")
        logger.debug(f"вернул товары, от которых отказались, на полку из заказа {order_id}")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/users', methods=['GET', 'POST'])
def users():
    return render_template('admin_not-ready.html')
    # return render_template('admin_users.html')


@app.route('/users/delete/<users_id>', methods=['DELETE'])
def users_delete(users_id):
    """Delete order from database"""
    logger.debug(f"Removing user with id: {users_id}")
    try:
        Database().execute(f"DELETE FROM users WHERE order_id={users_id};")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/add_items', methods=['GET', 'POST'])
def add_items():
    dollar = Database().execute("Select * from dollar where id = 1", 'fetchone')
    match request.method:
        case 'POST':
            form = request.form.to_dict()
            logger.debug(form)

            logger.debug('Добавляем новый продукт')
            if 'productName' in form:
                name = form['productName']
                category_id = int(form['productCategory'])
                brand = form['productBrand']
                description = form.get('productDescription', '')
                by_price = float(form['productByPrice'])
                if form.get('productDollar', None) == 'on':
                    in_dollar = True
                    sell_price = round(by_price * dollar['price'] * 1.5, 0)
                else:
                    in_dollar = False
                    sell_price = round(by_price * 1.5, 0)
                amount = form.get('productAmount', 0)
                image = form.get('productImagePath', '../../static/images/products/products-blank.png')

                Database().execute(
                    "INSERT INTO products "
                    "(name, by_price, price, amount, brand, price_dependency, category_id, "
                    "description, image_path) "
                    f"VALUES "
                    f"('{name}', {by_price}, {sell_price}, {amount}, '{brand}', {in_dollar}, {category_id}, "
                    f"'{description}', '{image}');")

            if 'categoryName' in form:
                logger.debug('Добавляем новую категорию')
                parent_id = form['categoryParentId']
                name = form['categoryName']
                image = form.get('productImagePath', '')
                Database().execute("INSERT INTO categories (parent_id, name, image_path) "
                                   f"VALUES({parent_id}, '{name}', '{image}');")

    categories_list = Database().execute("Select * from categories", 'fetchall')
    return render_template('admin_add_items.html',
                           categories=categories_list,
                           dollar=dollar)


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(Tasks.update_dollar_course, 'interval', hours=24)
    scheduler.start()
    logger.debug(scheduler.print_jobs())
    try:
        app.run(host='0.0.0.0', port=1112, debug=True)
    except KeyboardInterrupt:
        pass
    finally:
        logger.debug("scheduler: shutdown")
        scheduler.shutdown()


@app.errorhandler(404)
def page_not_found(error):
    """Страница 'страница не найдена'"""
    return render_template('admin_404.html'), 404


@app.errorhandler(500)
def error_page(error):
    """Страница 'страница не найдена'"""
    return render_template('user_500.html'), 500


@app.route('/error_500')
def nonexistent_page():
    """Пример эндпоинта, которого нет"""
    # Генерируем ошибку 404 "Страница не найдена"
    abort(500)


if __name__ == '__main__':
    main()
