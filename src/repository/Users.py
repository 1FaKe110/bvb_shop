class Users:

    @staticmethod
    def by_login(login):
        return (f"Select login, password "
                f"from users_new "
                f"where login = '{login}'")

    @staticmethod
    def by_email(email):
        return (f"Select u.email, fio "
                f"from users_new u "
                f"where email = '{email}'")

    @staticmethod
    def by_login_extended(login):
        return (f"SELECT id, fio, login, phone, email, is_registered "
                f"FROM users_new "
                f"WHERE login = '{login}'")

    @staticmethod
    def by_phone(phone):
        return (f"Select * "
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
    def update_password(password, email):
        return ("UPDATE public.users_new "
                f"SET password='{password}' "
                f"where email='{email}'")

    @staticmethod
    def new_user(username, phone, email, password, fio):
        return ("INSERT INTO users_new "
                "(login, phone, email, password, is_registered, fio) "
                "VALUES "
                f"('{username}', '{phone}', '{email}', '{password}', true, '{fio}');")
