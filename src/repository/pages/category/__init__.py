import json

from flask import render_template, request, Blueprint
from loguru import logger

from assets.assets import check_session
from database import db
from repository.sql import DbQueries
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
category_page = Blueprint('category_page', __name__)


class Category:

    def __init__(self):
        pass

    @staticmethod
    def render_page(session, category_name):
        # Получение выбранной категории
        category = db.exec(
            DbQueries.Categories.Select.all_by_category_name(category_name),
            'fetchone')

        prev_category = db.exec(
            DbQueries.Categories.Select.prev_category_name(category_name),
            'fetchone')

        logger.debug(f'Проверяю наличие подкатегорий у {category_name}: [{category}]')
        logger.debug(f'Родительская категория {prev_category}')

        if prev_category is None:
            prev_category = ''

        if category is not None:
            logger.debug(f'У {category_name} есть подкатегории')
            subcategories = db.exec(
                DbQueries.Categories.Select.sub_categories_by_parent_id(category.parent_id),
                'fetchall')

            products = db.exec(
                DbQueries.Products.Select.all_by_category_id(category.parent_id),
                'fetchall')  # Получение товаров в выбранной категории

            return render_template('category.html',
                                   prev_category=prev_category,
                                   category_name=category_name,
                                   subcategories=subcategories,
                                   products=products,
                                   login=check_session(session))

        subcategories = None
        cookies = request.cookies.get('formData', '{}')
        cart_data = json.loads(cookies)
        products = db.exec(
            DbQueries.Products.Select.all_by_category_name(category_name),
            'fetchall')  # Получение товаров в выбранной категории

        if products is None:
            return render_template('category.html',
                                   prev_category=prev_category,
                                   category_name=category_name,
                                   subcategories=subcategories,
                                   products=products,
                                   login=check_session(session))

        if not len(cart_data):
            return render_template('category.html',
                                   prev_category=prev_category,
                                   category_name=category_name,
                                   subcategories=subcategories,
                                   products=products,
                                   login=check_session(session))

        for _product in products:
            if str(_product.id) in cart_data:
                _product.in_card = cart_data[str(_product.id)]
                logger.debug(f"id: {_product.id} | {_product.name} | {_product.in_card} in card")

        return render_template('category.html',
                               prev_category=prev_category,
                               category_name=category_name,
                               subcategories=subcategories,
                               products=products,
                               login=check_session(session))
