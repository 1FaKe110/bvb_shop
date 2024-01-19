import hashlib

from flask import redirect, url_for, render_template, request, Blueprint, flash
from loguru import logger

from repository.database import db
from repository.sql import DbQueries
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
registry_page = Blueprint('registry_page', __name__)


class Registry:

    def __init__(self):
        pass

    @staticmethod
    def render_page():
        return render_template('register.html')

    @staticmethod
    def create_new_user(session):
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        fio = request.form['fio']
        phone = request.form['phone']
        email = request.form['email']

        # Проверка на наличие пользователя в бд по номеру телефона
        user_info = db.exec(
            DbQueries.Users.Select.all_by_login(username),
            'fetchall'
        )
        if user_info is not None:
            logger.error(f'Имя пользователя: {username} Занято')
            flash('Пользователь с таким логином уже существует', 'error')
            return render_template('register.html')

        user_info = db.exec(
            DbQueries.Users.Select.all_by_phone(phone),
            'fetchone'
        )
        logger.debug(user_info)
        if user_info is None:
            logger.info('Новый номер телефона. такого пользователя не было')
            db.exec(
                DbQueries.Users.Insert.new_user(
                    username, phone, email, hashed_password, fio
                )
            )
            session['username'] = username  # устанавливаем сессию
            return redirect(url_for('main_page.profile'))

        logger.error(f"Пользователь с таким телефоном существует: {user_info.is_registered}")

        if user_info.is_registered:
            logger.debug("Пользователь зарегистрирован")
            if user_info.email == email:
                logger.error('Пользователь с такой почтой уже существует')
                flash('Пользователь с такой почтой уже существует', 'error')
                return render_template('register.html')

            if user_info.phone == phone:
                logger.error('Пользователь с таким номером телефона уже существует')
                flash('Пользователь с таким номером телефона уже существует', 'error')
                return render_template('register.html')
        else:
            logger.info("есть данные по пользователю, но он не зарегистрирован")

        session['username'] = username
        db.exec(
            DbQueries.Users.Update.register_by_id(
                fio, hashed_password, email, phone, username, user_info.id
            )
        )
        return redirect(url_for('main_page.profile'))
