class Products:

    class Select:
        @staticmethod
        def all_by_category_id(category_id):
            return (f"SELECT * "
                    f"FROM products "
                    f"WHERE category_id = '{category_id}' "
                    f"ORDER BY id")

        @staticmethod
        def random(limit):
            return (f"SELECT * "
                    f"FROM products p "
                    f"where p.amount > 0 "
                    f"ORDER BY RANDOM() "
                    f"LIMIT {limit};")

        @staticmethod
        def by_rating(limit):
            return ("select "
                    "p.*, AVG(r.rating) as average_rating "
                    "from products p "
                    "inner join reviews r on p.id = r.product_id "
                    "group by p.id, p.name "
                    "order by average_rating desc "
                    f"limit {limit};")

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
                    f"order by id ")

        @staticmethod
        def all_by_category_name(category_name):
            return (f"SELECT * "
                    f"FROM products "
                    f"WHERE category_id in "
                    f"(SELECT id FROM categories WHERE LOWER(name) = '{category_name.lower()}') "
                    f"ORDER BY id")

        @staticmethod
        def by_name_and_product_id(name, product_id):
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
        def all_products_joined_categories_and_brands():
            return ("select p.id as p_id, "
                    "p.name as name, "
                    "p.price as price, "
                    "p.amount as amount, "
                    "p.image_path as image_path, "
                    "p.brand as brand, "
                    "c.name as c_name, "
                    "c.parent_id as c_parent_id "
                    "from products p "
                    "inner join categories c on p.category_id = c.id "
                    "inner join brands b on p.brand = b.name "
                    "order by p.id ")

    class Update:

        @staticmethod
        def amount_by_id(idx, new_amount):
            return (f"UPDATE products "
                    f"SET amount={new_amount} "
                    f"WHERE id={idx};")


    @staticmethod
    def all_products_joined_categories_and_brands():
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
                "order by p.id ")
