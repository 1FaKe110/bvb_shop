from datetime import datetime


class DbQueries:
    class Users:

        @staticmethod
        def by_login(login):
            return (f"Select login, password "
                    f"from users_new "
                    f"where login = '{login}'")

        @staticmethod
        def by_login_extended(login):
            return (f"SELECT id, fio, login, phone, email, is_registered "
                    f"FROM users_new "
                    f"WHERE login = '{login}'")

        @staticmethod
        def by_phone(phone):
            return (f"Select id "
                    f"from users_new "
                    f"where phone = '{phone}'")

        @staticmethod
        def register_by_id(fio, password, email, phone, username, user_id):
            return ("UPDATE public.users_new "
                    f"SET fio='{fio}', "
                    f"password='{password}', "
                    f"email='{email}', "
                    f"phone='{phone}', "
                    "is_admin=false, "
                    "is_registered=true, "
                    f"login='{username}' "
                    f"WHERE id={user_id};")

        @staticmethod
        def new_user(username, phone, email, password, fio):
            return ("INSERT INTO users_new "
                    "(login, phone, email, password, is_registered, fio) "
                    "VALUES "
                    f"('{username}', '{phone}', '{email}', '{password}', true, '{fio}');")

    class Orders:

        class Insert:

            @staticmethod
            def new_order(order_id, user_id, position_id,
                          product_price, product_amount,
                          order_place, order_time):
                return ('INSERT into orders '
                        '(order_id, user_id, status_id, position_id, '
                        'position_price, amount, address, datetime, creation_time) '
                        'values '
                        f"({order_id}, {user_id}, 001, {position_id}, {product_price}, {product_amount}, "
                        f"'{order_place}', '{order_time}', '{datetime.now().isoformat()}')")

        class Update:

            @staticmethod
            def update_position_amount(idx, amount):
                return (f"update public.orders "
                        f"set amount = {amount} "
                        f"where id = {idx}")

        @staticmethod
        def positions_by_order_id(order_id):
            return (f"select id, position_id, amount "
                    f"from orders o "
                    f"where order_id = {order_id} "
                    f"ORDER BY position_id asc")

        @staticmethod
        def by_user_id(user_id):
            return (f"select distinct(o.order_id), "
                    f"o.address, "
                    f"cast(datetime as text), "
                    f"cast(o.creation_time as text), "
                    f"o.status_id, "
                    f"os.name "
                    f"from orders o "
                    f"inner join order_status os on os.id = o.status_id "
                    f"where user_id = {user_id} "
                    f"order by o.order_id desc")

        @staticmethod
        def profile_order(order_id, user_id):
            return (f"select distinct(o.order_id), "
                    f"o.status_id, "
                    f"os.name as status_name, "
                    f"o.address, "
                    f"cast(cast(o.datetime as date) as text), "
                    f"cast(o.creation_time as text) "
                    f"from orders o "
                    f"inner join order_status os on os.id = o.status_id "
                    f"where true "
                    f"and order_id = {order_id} "
                    f"and user_id = {user_id}")

        @staticmethod
        def profile_order_positions(order_id, user_id):
            return (f"select o.position_id as id, "
                    f"o.position_price as price, "
                    f"o.amount, "
                    f"p.amount as total_amount, "
                    f"p.name "
                    f"from orders o "
                    f"inner join products p on p.id = o.position_id "
                    f"where true "
                    f"and order_id = {order_id} "
                    f"and user_id = {user_id}")

    class Products:
        class Update:

            @staticmethod
            def amount_by_id(idx, new_amount):
                return (f"UPDATE products "
                        f"SET amount={new_amount} "
                        f"WHERE id={idx};")

        @staticmethod
        def by_id(idx):
            return (f"SELECT * "
                    f"FROM products "
                    f"WHERE id = {idx}")

        @staticmethod
        def by_id_list(ids):
            return (f"SELECT * "
                    f"FROM products "
                    f"WHERE id in ({','.join(ids)}) "
                    f"order by id asc")

        @staticmethod
        def by_category(category_name):
            return (f"SELECT * "
                    f"FROM products "
                    f"WHERE category_id in "
                    f"(SELECT id FROM categories WHERE name='{category_name}') "
                    f"ORDER BY id")

        @staticmethod
        def by_name_and_id(name, product_id):
            return (f"SELECT * "
                    f"FROM products "
                    f"WHERE name = '{name}' "
                    f"and id = {product_id} "
                    f"LIMIT 1")

    class Categories:

        @staticmethod
        def main():
            return ('SELECT * '
                    'FROM categories '
                    'WHERE parent_id is Null '
                    'ORDER BY id')

        @staticmethod
        def by_category(name):
            return (f"SELECT * "
                    f"FROM categories "
                    f"WHERE parent_id = (SELECT id FROM categories WHERE name='{name}') "
                    f"ORDER BY id")

        @staticmethod
        def by_id(category_id):
            return (f"SELECT name "
                    f"FROM categories "
                    f"WHERE id = '{category_id}'")

        @staticmethod
        def prev_category_name(name):
            return (f"SELECT name "
                    f"FROM categories c "
                    f"where id = (SELECT parent_id FROM categories WHERE name = '{name}') "
                    f"ORDER BY id")

        @staticmethod
        def check_sub_categories(parent_id):
            return (f"SELECT * "
                    f"FROM categories "
                    f"WHERE parent_id = '{parent_id}' "
                    f"ORDER BY id")

    class Addresses:

        @staticmethod
        def by_user_id(user_id):
            return (f"select * "
                    f"from addresses "
                    f"where user_id = {user_id}")

        @staticmethod
        def by_login(login):
            return ("select address "
                    "from addresses a "
                    "inner join users_new un on un.id = a.user_id  "
                    f"where un.login = '{login}'")
