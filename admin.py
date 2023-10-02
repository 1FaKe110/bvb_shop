import json

import flask
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_cors import CORS
from database import db
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from background import Tasks
from munch import DefaultMunch

as_class = DefaultMunch.fromDict

Tasks.update_dollar_course()
app = Flask(__name__)
CORS(app)


@logger.catch
@app.route('/')
def index():
    return redirect(url_for('categories'))


@logger.catch
@app.route('/categories', methods=['GET', 'POST'])
def categories():
    match request.method:
        case 'POST':
            form = as_class(request.form.to_dict())
            logger.debug(form)

            logger.debug('Меняем что-то в категориях')
            ct_id = form.ct_id.replace('.', '')
            ct_name = form.ct_name
            ct_image_path = form.categoryImagePath
            db.exec(
                f"UPDATE categories SET name='{ct_name}', image_path='{ct_image_path}' WHERE id={ct_id};"
            )

    categories_list = db.exec("Select * from categories order by id asc", 'fetchall')
    return render_template('admin_categories.html',
                           categories=categories_list)


@app.route('/categories/<category_id>/delete', methods=['DELETE'])
def categories_delete(category_id):
    """Delete product from database"""
    logger.debug(f"Removing categories with id: {category_id}")
    try:
        db.exec(f"DELETE FROM categories WHERE id={category_id};")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/products', methods=['GET', 'POST'])
def products():
    match request.method:
        case 'POST':
            form = as_class(request.form.to_dict())
            logger.debug(form)

            logger.debug('Меняем что-то в продуктах')

            db.exec(
                f"UPDATE products SET "
                f"name='{form.pr_name}', "
                f"by_price={form.pr_by_price}, "
                f"price={form.pr_price}, "
                f"amount={form.pr_amount}, "
                f"brand='{form.pr_brand}', "
                f"price_dependency={form.pr_price_dependency}, "
                f"category_id={form.categoryParentName}, "
                f"image_id=Null, "
                f"description='{form.pr_description}', "
                f"image_path='{form.categoryImagePath}' "
                f"WHERE id={form.pr_id}; "
            )

    dollar = db.exec("Select * from dollar where id = 1", 'fetchone')
    products_list = db.exec("Select * from products order by name asc", 'fetchall')
    categories_list = db.exec("Select * from categories order by id asc", 'fetchall')
    return render_template('admin_products.html',
                           categories=categories_list,
                           products=products_list,
                           dollar=dollar)


@app.route('/products/<product_id>/delete', methods=['DELETE'])
def products_delete(product_id):
    """Delete product from database"""
    logger.debug(f"Removing product with id: {product_id}")
    try:
        db.exec(f"DELETE FROM products WHERE id={product_id};")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    match request.method:
        case 'POST':
            form = as_class(request.form.to_dict())
            logger.debug(json.dumps(form, indent=2, ensure_ascii=False))
            logger.debug('Меняем что-то в заказах')

    orders_list = as_class(db.exec(
        "Select distinct(order_id), user_id, status_id, address, cast(datetime as text), "
        "ose.id as status_id, ose.name "
        "from orders o "
        "inner join order_status ose on ose.id = o.status_id "
        "order by order_id asc",
        'fetchall'))
    for order_obj in orders_list:
        order_obj.datetime = order_obj.datetime[:10]
        order_obj.sum = 0
        order_obj.positions = as_class(db.exec(
            "select p.id as id, "
            "p.name as name, "
            "p.price as price, "
            "o.amount as amount "
            "from orders o "
            "LEFT JOIN products p on p.id = o.position_id "
            "WHERE TRUE "
            f"and order_id = {order_obj.order_id} "
            f"order by order_id asc",
            "fetchall"
        ))
        for position in order_obj.positions:
            order_obj.sum += position.price * position.amount

    order_statuses = db.exec("Select * from order_status", 'fetchall')
    return render_template('admin_orders.html',
                           orders=orders_list,
                           order_statuses=order_statuses)


@logger.catch
@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order(order_id):
    match request.method:
        case 'POST':
            form = as_class(request.form.to_dict())
            logger.debug(json.dumps(form.__dict__, indent=2, ensure_ascii=False))
            logger.debug('Меняем что-то в заказах')

    order_obj = as_class(db.exec(
        "Select distinct(order_id), "
        "status_id, address, "
        "cast(datetime as text), "
        "ose.id as status_id, "
        "ose.name as status_name, u.username, "
        "u.phone, u.email "
        "from orders o "
        "inner join order_status ose on ose.id = o.status_id "
        "inner join users u on o.user_id = u.id "
        f"where order_id = {order_id}",
        'fetchone'))

    if not len(order_obj):
        return redirect(url_for('orders'))

    order_obj.datetime = order_obj.datetime[:10]
    order_obj.sum = 0
    order_obj.positions = as_class(db.exec(
        "select p.id as id, "
        "p.name as name, "
        "p.price as price, "
        "o.amount as amount "
        "from orders o "
        "LEFT JOIN products p on p.id = o.position_id "
        "WHERE TRUE "
        f"and order_id = {order_id};",
        "fetchall"
    ))
    for position in order_obj.positions:
        order_obj.sum += position.price * position.amount

    logger.debug(json.dumps(order_obj, indent=2, ensure_ascii=False))
    order_statuses = db.exec("Select * from order_status order by id asc", 'fetchall')
    return render_template('admin_order_detailed.html',
                           order=order_obj,
                           order_statuses=order_statuses)


@app.route('/order/<order_id>/delete', methods=['DELETE'])
def order_delete(order_id):
    """Delete order from database"""
    logger.debug(f"Removing order with id: {order_id}")

    try:
        db.exec(f"UPDATE orders SET status_id=4 WHERE order_id={order_id};")
        item_list = db.exec(f"SELECT o.position_id as opid, o.amount as oam, p.amount as pam "
                            "from orders o "
                            "inner join products p on p.id = o.position_id "
                            f"where order_id={order_id};")
        for item in item_list:
            total_price = item['oam'] + item['pam']
            db.exec(f"UPDATE products SET amount={total_price} WHERE id={item['opid']};")

        logger.debug("вернул товары из удаленного заказа на полки")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@app.route('/order/<order_id>/update', methods=['POST'])
def order_update(order_id):
    """update order in database"""
    logger.debug(f"updating order with id: {order_id}")

    logger.debug(json.dumps(request.json, indent=2, ensure_ascii=False))
    data = as_class(request.json)

    db.exec(f"UPDATE public.users "
            f"SET username='{data.user.fio}', "
            f"phone='{data.user.phone}', "
            f"email='{data.user.email}'"
            f"WHERE id={order_id};")

    for pos in data.positions:
        pr_reply = as_class(
            db.exec(f"SELECT o.position_id as opid, "
                    f"o.amount as oam, "
                    f"p.amount as pam "
                    "from orders o "
                    "inner join products p on p.id = o.position_id "
                    f"where o.order_id={order_id} and o.position_id={pos.Id};",
                    'fetchall'))

        o_delta = pr_reply.oam - pos.Amount
        if pr_reply.pam - o_delta == 0:
            pass
        elif pr_reply.pam - o_delta < 0:
            logger.error(f"Попытка списания товара #{pr_reply.opid}, которого не хватит на {pr_reply.pam}")
            return flask.Response(status=500)




@logger.catch
@app.route('/order/<order_id>/delete/<item_id>', methods=['DELETE'])
def order_delete_item(order_id, item_id):
    """Delete order from database"""
    logger.debug(f"Removing item #{item_id} from order_id #{order_id}")
    try:
        item_list = as_class(db.exec(f"SELECT o.position_id as opid, "
                                     f"o.amount as oam, p.amount as pam "
                                     "from orders o "
                                     "inner join products p on p.id = o.position_id "
                                     f"where o.order_id={order_id} and o.position_id={item_id};",
                                     'fetchall'))
        db.exec(f"DELETE FROM orders WHERE order_id={order_id} and position_id={item_id};")
        for item in item_list:
            total_amount = item.oam + item.pam
            db.exec(f"UPDATE products SET amount={total_amount} WHERE id={item.opid};")

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
        db.exec(f"DELETE FROM users WHERE order_id={users_id};")
        return flask.Response(status=200)
    except Exception as ex_:
        logger.error(ex_)
        return flask.Response(status=500)


@logger.catch
@app.route('/add_items', methods=['GET', 'POST'])
def add_items():
    dollar = as_class(db.exec("SELECT id, price FROM dollar WHERE id=1;", 'fetchone'))
    logger.debug(f'dollar: {dollar}')
    match request.method:
        case 'POST':
            form = as_class(request.form.to_dict())
            logger.debug(form)

            logger.debug('Добавляем новый продукт')
            if 'productName' in form:
                name = form.productName
                category_id = int(form.productCategory)
                brand = form.productBrand
                description = form.productDescription
                by_price = float(form.productByPrice)
                if form.productDollar:
                    in_dollar = True
                    sell_price = round(by_price * dollar.price * 1.5, 0)
                else:
                    in_dollar = False
                    sell_price = round(by_price * 1.5, 0)

                amount = form.productAmount
                image = form.productImagePath

                db.exec(
                    "INSERT INTO products "
                    "(name, by_price, price, amount, brand, price_dependency, category_id, "
                    "description, image_path) "
                    f"VALUES "
                    f"('{name}', {by_price}, {sell_price}, {amount}, '{brand}', {in_dollar}, {category_id}, "
                    f"'{description}', '{image}');")

            if 'categoryName' in form:
                logger.debug('Добавляем новую категорию')

                parent_id = form.categoryParentId
                name = form.categoryName
                image = form.productImagePath
                db.exec("INSERT INTO categories (parent_id, name, image_path) "
                        f"VALUES({parent_id}, '{name}', '{image}');")

    categories_list = db.exec("Select * from categories", 'fetchall')
    return render_template('admin_add_items.html',
                           categories=categories_list,
                           dollar=dollar)


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(Tasks.update_dollar_course, 'interval', hours=24)
    scheduler.start()
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
