import datetime
import hashlib
import json
import secrets

from flask import redirect, url_for, render_template, request, Blueprint, flash
from loguru import logger

from assets.assets import check_session
from database import db
from repository.sql import DbQueries
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
profile_page = Blueprint('profile_page', __name__)


class Profile:

    def __init__(self):
        self.password_reset_tokens = {}

    @staticmethod
    def render_page(session):
        if 'username' not in session:
            logger.debug("Попытка перехода в профиль для не залогиненного пользователя. "
                         "перевожу на страницу авторизации")
            return redirect(url_for('main_page.login'))

        user_info = db.exec(
            DbQueries.Users.Select.all_by_login(session['username']),
            'fetchone'
        )

        if user_info is None:
            logger.warning("Проверь код. Пользователь с активной сессией, которого нет в бд!")
            return redirect(url_for('main_page.logout'))

        user_orders = db.exec(
            DbQueries.Orders.Select.by_user_id(user_info.id),
            'fetchall'
        )

        user_addresses = db.exec(
            DbQueries.Addresses.Select.by_user_id(user_info.id),
            'fetchall'
        )
        return render_template('profile.html',
                               user_info=user_info,
                               orders=user_orders,
                               addresses=user_addresses,
                               login=True)

    @staticmethod
    def get_order_detailed_page(session, order_id):
        if 'username' not in session:
            logger.debug("Попытка перехода в детальный просмотр заказа для не залогиненного пользователя. "
                         "перевожу на страницу авторизации")
            return redirect(url_for('main_page.login'))

        user = db.exec(
            DbQueries.Users.Select.id_and_password_by_login(session['username']),
            'fetchone'
        )
        user_order = db.exec(
            DbQueries.Orders.Select.profile_order(order_id, user.id),
            'fetchone'
        )

        if user_order is None:
            logger.debug(f"Данные по заказу #{order_id} у пользователя {user.id = } не найдены")
            flash("Вы пытаетесь перейти на заказ другого пользователя! Не надо так :)", 'error')
            return redirect(url_for('main_page.profile'))

        user_order.positions = db.exec(
            DbQueries.Orders.Select.profile_order_positions(order_id, user.id),
            'fetchall')

        order_sum = 0
        order_pos_count = 0
        for pos in user_order.positions:
            order_sum += pos.price * pos.amount
            order_pos_count += pos.amount

        user_order.positions.append(
            as_class(
                dict(id='Итого', price=f'{order_sum} р.',
                     amount=order_pos_count,
                     name='', total_amount=None)
            )
        )

        logger.debug(
            json.dumps(
                user_order.__dict__, indent=2, ensure_ascii=False
            )
        )

        return render_template('profile_order_detailed.html',
                               order=user_order,
                               login=check_session(session))

    def render_new_password_page(self, session, token):
        self.check_active_tokens(session, token)
        return render_template('set_new_password.html', token=token)

    def update_user_password(self, session, token):
        self.check_active_tokens(session, token)

        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        email = self.password_reset_tokens[token]["email"]

        db.exec(
            DbQueries.Users.Update.password_by_email(hashed_password, email)
        )

        logger.info(f'удаляю все токены для сброса пароля по [{email}]')
        del self.password_reset_tokens[token]
        [self.password_reset_tokens.pop(t) for t in self.password_reset_tokens
         if self.password_reset_tokens[t]['email'] == email]

        logger.info('Токены удалены')
        return redirect(url_for('main_page.login', login=check_session(session)))

    @staticmethod
    def render_recover_password_page():
        return render_template('recover_password.html')

    def recover_password_send_notify(self, session, mailer):

        email = request.form['email']
        user = db.exec(
            DbQueries.Users.Select.email_and_fio_by_email(email),
            'fetchone'
        )

        if user is None:
            flash("Такой почты нет!", 'error')
            return render_template('recover_password.html')

        token = secrets.token_urlsafe(16)
        self.password_reset_tokens[token] = {
            "email": email,
            "timestamp": datetime.datetime.now()
        }

        mailer.recover_password(user.email, user.fio, token)
        flash(f'Сообщение о смене пароля отправлено на почту {email}', 'info')
        return redirect(url_for('main_page.login', login=check_session(session)))

    def check_active_tokens(self, session, token):
        if token not in self.password_reset_tokens:
            message = "Ссылка для сброса пароля недействительна или устарела"
            logger.debug(message)
            flash(message, 'error')
            return redirect(url_for('main_page.login', login=check_session(session)))
