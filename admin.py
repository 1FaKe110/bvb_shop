from flask import Flask, render_template, request, redirect, url_for
from database import Database
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from background import Tasks
from database.filler import reset_database

RESET_DB = False
if RESET_DB:
    reset_database()

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
            Database().execute(
                f"UPDATE categories SET name='{form['ct-name']}' WHERE id={ct_id};"
            )

    categories_list = Database().execute("Select * from categories", 'fetchall')
    return render_template('admin_categories.html',
                           categories=categories_list)


@logger.catch
@app.route('/products', methods=['GET', 'POST'])
def products():
    match request.method:
        case 'POST':
            form = request.form.to_dict()
            logger.debug(form)

            logger.debug('Меняем что-то в категориях')
            pr_id = form.get('pr-id').replace('.', '')
            Database().execute(
                f"UPDATE products SET "
                f"name='{form['ct-name']} "
                f"brand='{form['ct-name']} "
                f"WHERE id={pr_id};"
            )

    dollar = Database().execute("Select * from dollar where id = 1", 'fetchone')
    products_list = Database().execute("Select * from products", 'fetchall')
    categories_list = Database().execute("Select * from categories", 'fetchall')
    return render_template('admin_products.html',
                           categories=categories_list,
                           products=products_list,
                           dollar=dollar)


@logger.catch
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    orders_list = Database().execute(
        "Select distinct(order_id), user_id, status_id, address, datetime, ose.id as status_id, ose.name "
        "from orders o "
        "inner join order_status_enum ose on ose.id = o.status_id ",
        'fetchall')
    for order in orders_list:
        order['positions'] = Database().execute(
            "select p.id as id, "
            "p.name as name, "
            "p.price as price, "
            "o.amount as amount "
            "from orders o "
            "LEFT JOIN products p on p.id = o.position_id "
            "WHERE TRUE "
            f"and order_id = {order['order_id']};",
            "fetchall"
        )

    order_statuses = Database().execute("Select * from order_status_enum", 'fetchall')
    return render_template('admin_orders.html',
                           orders=orders_list,
                           order_statuses=order_statuses)


@logger.catch
@app.route('/users', methods=['GET', 'POST'])
def users():
    return render_template('admin_users.html')


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
                category = int(form['productCategory'])
                brand = form['productBrand']
                description = form.get('productBrand', '')
                by_price = float(form['productByPrice'])
                if form['productDollar'] == 'on':
                    in_dollar = True
                    sell_price = round(by_price * dollar['price'] * 1.5, 0)
                else:
                    in_dollar = False
                    sell_price = round(by_price * 1.5, 0)
                amount = form.get('amount', 0)
                image = form.get('productImagePath', 'Null')

                Database().execute(
                    "INSERT INTO products "
                    "(name, by_price, price, amount, brand, price_dependency, category_id, image_id, description, "
                    "image_path) "
                    f"VALUES ('{name}', {by_price}, {sell_price}, {amount}, '{brand}', {in_dollar}, {category}, Null, '{description}', '{image}');")

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


if __name__ == '__main__':
    main()
