import re


class Review:
    class Insert:
        @staticmethod
        def new(user_id, review_text, rating, review_date, product_id):
            return (
                "INSERT INTO reviews "
                "(user_id, review_text, rating, review_date, product_id) "
                f"VALUES "
                f"({user_id}, '{re.escape(review_text)}', {rating}, '{review_date}', {product_id})"
            )

    class Select:

        @staticmethod
        def review_by_product_id(product_id):
            return (
                "Select "
                "u.fio as full_name, "
                "r.rating as rating, "
                "cast(cast(r.review_date as date) as text) as review_date, "
                "r.review_text as review_text "
                "from reviews r "
                "inner join users_new u on r.user_id = u.id "
                f"where r.product_id = '{product_id}' "
                f"order by r.review_date desc"
            )