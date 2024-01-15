from flask import redirect, url_for, Blueprint
from loguru import logger
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
logout_page = Blueprint('logout_page', __name__)


class Logout:

    def __init__(self):
        pass

    @staticmethod
    def close_user_session(session):
        logger.debug(f"removing {session['username']} from active sessions")
        session.pop('username', None)
        return redirect(url_for('main_page.index'))
