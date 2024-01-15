from datetime import datetime


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

    class Select:

        @staticmethod
        def last_order_id():
            return (f"Select max(order_id) as id "
                    f"from orders")
        @staticmethod
        def positions_by_order_id(order_id):
            return (f"select id, position_id, amount "
                    f"from orders o "
                    f"where order_id = {order_id} "
                    f"ORDER BY position_id")

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
