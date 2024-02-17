import os

import flask
from munch import DefaultMunch
from flask_cors import CORS
from flask import Flask, request, session

from assets.assets import *
from repository.database import db
from loguru import logger

from repository.mail import Mailer
from repository.pages import Pages
from repository.pages.main_page import main_page
from repository.telegram_bot.Bot import Telebot
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': os.getenv('elastic_host'), 'port': os.getenv('elastic_port')}])
as_class = DefaultMunch.fromDict
app = Flask(__name__)
app.secret_key = os.getenv('secret_key')  # секретный ключ для сессий
CORS(app)
bot = Telebot()
mailer = Mailer()
pages = Pages()


@main_page.route('/login', methods=['GET', 'POST'])
def login():
    """Обработчик для входа"""
    match request.method:
        case 'GET':
            return pages.login.handler.render_page()
        case 'POST':
            return pages.login.handler.process_login(session)
        case _:
            return flask.Response(status=405)


@main_page.route('/logout')
def logout():
    """Выход из личного кабинета"""
    match request.method:
        case 'GET':
            return pages.logout.handler.close_user_session(session)
        case _:
            return flask.Response(status=405)


@main_page.route('/register', methods=['GET', 'POST'])
def register():
    """Обработчик для регистрации"""
    match request.method:
        case 'GET':
            return pages.registry.handler.render_page()
        case 'POST':
            return pages.registry.handler.create_new_user(session)
        case _:
            return flask.Response(status=405)


# Маршрут для выполнения поисковых запросов
@main_page.route('/search', methods=['GET'])
def search():
    match request.method:
        case 'GET':
            return pages.search.handler.get_search_page(session, es)
        case _:
            return flask.Response(status=405)


@main_page.route('/search-helper', methods=['GET'])
def search_helper():
    """ Подсказки для поисковой строки """
    match request.method:
        case 'GET':
            return pages.search.handler.get_annotations(es)
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/')
def index():
    """# Определение маршрута Flask для главной страницы"""
    match request.method:
        case 'GET':
            return pages.main_page.handler.render_main_page(session)
        case _:
            return flask.Response(status=405)


@main_page.errorhandler(404)
def page_not_found(error):
    """Страница 'страница не найдена'"""
    match request.method:
        case 'GET':
            pages.main_page.handler.page_not_found()
        case _:
            return flask.Response(status=405)


@main_page.errorhandler(500)
def error_page(error):
    """Страница 'Произошла ошибка'"""
    match request.method:
        case 'GET':
            pages.main_page.handler.page_not_found()
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/category/<string:category_name>')
def category(category_name):
    """# Определение маршрута Flask для путешествия по иерархии категорий"""
    match request.method:
        case 'GET':
            return pages.category.handler.render_page(session, category_name)
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/product/<product_name>/<product_id>')
def product(product_name, product_id):
    """# Определение маршрута Flask для просмотра товара"""
    match request.method:
        case 'GET':
            return pages.product.handler.get_page(session, product_name, product_id)
        case _:
            return flask.Response(status=405)


@main_page.route('/get_reviews/<product_id>')
def get_review(product_id):
    match request.method:
        case 'GET':
            return pages.product.handler.get_reviews(product_id)
        case _:
            return flask.Response(status=405)


@main_page.route('/add_review', methods=['POST'])
def add_review():
    match request.method:
        case 'POST':
            return pages.product.handler.add_review(session)
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/cart/', methods=['GET', 'POST'])
def cart(error_description=None):
    """Получение данных корзины из cookies где ключом будет id товара, а значением кол-во"""
    match request.method:
        case 'GET':
            return pages.cart.handler.get_page(session, error_description)
        case 'POST':
            return pages.cart.handler.add_new_order(session, bot)
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/cart/c/', methods=['GET', 'POST'])
def cart_clear():
    """Метод для очистки cookie фалов"""
    match request.method:
        case 'GET':
            return pages.cart.handler.clear_cookie_data(session)
        case _:
            return flask.Response(status=405)


@main_page.route('/profile')
def profile():
    """Страница профиля пользователя"""
    match request.method:
        case 'GET':
            return pages.profile.handler.render_page(session)
        case _:
            return flask.Response(status=405)


@main_page.route('/profile/order/<order_id>')
def profile_order_details(order_id):
    """Страница профиля пользователя"""
    match request.method:
        case 'GET':
            return pages.profile.handler.get_order_detailed_page(session, order_id)
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/about')
def about():
    """Старинца с информацией об организации"""
    match request.method:
        case 'GET':
            return pages.about.handler.render_page(session)
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/delivery')
def delivery():
    """Старинца с информацией о доставке"""
    match request.method:
        case 'GET':
            return pages.delivery.handler.render_page(session)
        case _:
            return flask.Response(status=405)


@main_page.route('/set_new_password/<token>', methods=['GET', 'POST'])
def set_new_password(token):
    match request.method:
        case 'GET':
            return pages.profile.handler.render_new_password_page(session, token)
        case 'POST':
            return pages.profile.handler.update_user_password(session, token)
        case _:
            return flask.Response(status=405)


@logger.catch
@main_page.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    match request.method:
        case 'GET':
            return pages.profile.handler.render_recover_password_page()
        case 'POST':
            return pages.profile.handler.recover_password_send_notify(session, mailer)
        case _:
            return flask.Response(status=405)


def main():
    app.register_blueprint(pages.main_page.page, url_prefix='/')
    app.register_blueprint(pages.login.page, url_prefix='/login')
    app.register_blueprint(pages.logout.page, url_prefix='/logout')
    app.register_blueprint(pages.registry.page, url_prefix='/registry')
    app.register_blueprint(pages.profile.page, url_prefix='/profile')
    app.register_blueprint(pages.category.page, url_prefix='/category')
    app.register_blueprint(pages.product.page, url_prefix='/product')
    app.register_blueprint(pages.cart.page, url_prefix='/cart')
    app.register_blueprint(pages.search.page, url_prefix='/search')
    app.register_blueprint(pages.about.page, url_prefix='/about')
    app.register_blueprint(pages.delivery.page, url_prefix='/delivery')

    if es.ping():
        logger.info("Connected to ElasticSearch")
        index_postgres_data_for_search(db, es)
    else:
        logger.error("Could not connect to ElasticSearch")

    app.run(host='0.0.0.0', port=1111, debug=True)


if __name__ == '__main__':
    main()
