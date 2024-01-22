from flask import render_template, Blueprint

from assets.assets import check_session
from repository.database import db
from repository.sql import DbQueries
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
main_page = Blueprint('main_page', __name__)


class MainPage:

    def __init__(self):
        pass

    @staticmethod
    def render_main_page(session):
        # Получение списка категорий верхнего уровня
        categories = db.exec(
            DbQueries.Categories.Select.main(),
            'fetchall')

        # выбираем 4 рандомных товара из бд
        products = db.exec(
            DbQueries.Products.Select.by_rating(4),
            'fetchall'
        )

        return render_template('index.html',
                               categories=categories,
                               products=products,
                               current_url='/category',
                               login=check_session(session))

    @staticmethod
    def page_not_found():
        return render_template('404.html'), 404

    @staticmethod
    def error_page():
        return render_template('500.html'), 500
