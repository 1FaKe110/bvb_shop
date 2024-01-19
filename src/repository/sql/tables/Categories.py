class Categories:
    class Select:

        @staticmethod
        def main():
            return ('SELECT * '
                    'FROM categories '
                    'WHERE parent_id is Null '
                    'ORDER BY id')

        @staticmethod
        def sub_categories_by_parent_id(parent_id):
            return (f"SELECT * "
                    f"FROM categories "
                    f"WHERE parent_id = '{parent_id}' "
                    f"ORDER BY id")

        @staticmethod
        def all_by_category_name(name):
            return (f"SELECT * "
                    f"FROM categories "
                    f"WHERE parent_id = (SELECT id FROM categories WHERE LOWER(name) = '{name.lower()}') "
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
        def all_order_by_id():
            return ("select c.id as c_id, "
                    "c.parent_id as c_parent_id, "
                    "c.name as c_name, "
                    "c.image_path as c_image_path "
                    "from categories c "
                    "order by id")
