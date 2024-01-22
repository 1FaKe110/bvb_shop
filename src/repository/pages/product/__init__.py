import datetime
from flask import render_template, request, Blueprint, jsonify
from loguru import logger

from assets.assets import check_session
from repository.database import db
from repository.sql import DbQueries
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
product_page = Blueprint('product_page', __name__)


class Product:

    def __init__(self):
        pass

    @staticmethod
    def get_page(session, product_name, product_id):
        if check_session(session):
            user = db.exec(
                DbQueries.Users.Select.id_and_password_by_login(session['username']),
                'fetchone'
            )
        else:
            user = None
            logger.debug("Пользователь не залогинен, отзыв оставить нельзя")

        product = db.exec(
            DbQueries.Products.Select.by_name_and_product_id(product_name, product_id),
            'fetchone')

        category_name = db.exec(
            DbQueries.Categories.Select.by_id(product.category_id),
            'fetchone')

        return render_template('product.html',
                               category_name=category_name.name,
                               product=product,
                               user=user,
                               current_url='/product',
                               login=check_session(session))

    @staticmethod
    def get_reviews(product_id):
        reviews = db.exec(
            DbQueries.Reviews.Select.review_by_product_id(product_id),
            'fetchall'
        )
        return jsonify(reviews)

    @staticmethod
    def add_review(session):
        if not check_session(session):
            return jsonify(
                dict(code='error', message="Нужно быть авторизованным пользователем,\n чтобы оставить отзыв")
            )

        # Получаем данные от пользователя
        data = as_class(request.get_json())
        logger.debug(f"Добавление нового отзыва для товара с id: {data.product_id}")

        try:
            db.exec(
                DbQueries.Reviews.Insert.new(
                    int(data.user_id), data.review_text, int(data.rating),
                    datetime.datetime.now().isoformat(), int(data.product_id)
                ))
            logger.info("Отзыв добавлен")
            return jsonify(dict(code='info', message="Отзыв успешно добавлен"))
        except Exception as ex:
            logger.error(ex)
            return jsonify(dict(code='error', message=f'Ошибка при добавлении отзыва \n {ex}'))
