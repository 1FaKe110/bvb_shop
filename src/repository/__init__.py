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
                    f"FROM users "
                    f"WHERE login = '{login}'")

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
        pass

    class Products:
        pass

    class Categories:
        pass
