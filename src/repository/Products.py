class Products:
    class Update:

        @staticmethod
        def amount_by_id(idx, new_amount):
            return (f"UPDATE products "
                    f"SET amount={new_amount} "
                    f"WHERE id={idx};")

    @staticmethod
    def random(limit):
        return (f"SELECT * "
                f"FROM products p "
                f"where p.amount > 0"
                f"ORDER BY RANDOM() "
                f"LIMIT {limit};")

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

    @staticmethod
    def by_brand(brand):
        return ("SELECT * "
                "FROM products "
                f"where brand like '%{brand}%'")

    @staticmethod
    def all():
        return ("select p.id as p_id, "
                "p.name as p_name, "
                "p.price as p_price, "
                "p.amount as p_amount, "
                "p.image_path as p_image_path, "
                "p.brand as p_brand, "
                "c.name as c_name, "
                "c.parent_id as c_parent_id "
                "from products p "
                "inner join categories c on p.category_id = c.id "
                "inner join brands b on p.brand = b.name "
                "order by p.id asc")