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
