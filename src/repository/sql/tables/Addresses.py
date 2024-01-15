class Addresses:
    class Insert:

        @staticmethod
        def new_address(user_id, address):
            return (f"INSERT INTO public.addresses "
                    f"(user_id, address) "
                    f"VALUES ({user_id}, '{address}');")

    class Select:
        @staticmethod
        def by_user_id(user_id):
            return (f"select * "
                    f"from addresses "
                    f"where user_id = {user_id}")

        @staticmethod
        def address_by_login(login):
            return ("select address "
                    "from addresses a "
                    "inner join users_new un on un.id = a.user_id  "
                    f"where un.login = '{login}'")

        @staticmethod
        def id_by_user_id_and_address(user_id, address):
            return (f"select id "
                    f"from public.addresses "
                    f"where true "
                    f"and user_id = {user_id} "
                    f"and address = '{address}'")
