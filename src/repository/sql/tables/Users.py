class Users:

    class Select:
        @staticmethod
        def id_and_password_by_login(login):
            return (f"Select id, login, password "
                    f"from users_new "
                    f"where login = '{login}'")

        @staticmethod
        def email_and_fio_by_email(email):
            return (f"Select u.email, fio "
                    f"from users_new u "
                    f"where email = '{email}'")

        @staticmethod
        def all_by_login(login):
            return (f"SELECT * "
                    f"FROM users_new "
                    f"WHERE login = '{login}'")

        @staticmethod
        def all_by_phone(phone):
            return (f"Select * "
                    f"from users_new "
                    f"where phone = '{phone}'")

    class Update:
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
        def password_by_email(password, email):
            return ("UPDATE public.users_new "
                    f"SET password='{password}' "
                    f"where email='{email}'")

    class Insert:

        @staticmethod
        def new_unregistered_user(phone, fio):
            return (f"INSERT into users_new "
                    f"(fio, phone) "
                    f"values "
                    f"('{fio}', '{phone}') "
                    f"returning id;")


        @staticmethod
        def new_user(username, phone, email, password, fio):
            return ("INSERT INTO users_new "
                    "(login, phone, email, password, is_registered, fio) "
                    "VALUES "
                    f"('{username}', '{phone}', '{email}', '{password}', true, '{fio}');")








