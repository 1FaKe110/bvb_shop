import hashlib

from flask import redirect, url_for, render_template, request, Blueprint, flash
from loguru import logger

from database import db
from repository.sql import DbQueries
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
login_page = Blueprint('login_page', __name__)


class Login:

    def __init__(self):
        pass

    @staticmethod
    def render_page():
        return render_template('login.html')

    @staticmethod
    def process_login(session):
        username = request.form['username']
        hashed_password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        logger.info(f'Хэш пароля: {hashed_password}')

        user_info = db.exec(
            DbQueries.Users.Select.id_and_password_by_login(username),
            "fetchone"
        )

        if user_info is None:
            logger.info('Пользователь не найден')
            flash('Пользователь не найден', 'error')
            return render_template('login.html')

        if user_info.password != hashed_password:
            logger.info('Не верный пароль')
            flash('Не верный логин или пароль', 'error')
            return render_template('login.html')

        session['username'] = username  # устанавливаем сессию
        return redirect(url_for('main_page.index'))
