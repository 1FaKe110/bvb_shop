from flask import render_template, Blueprint
from loguru import logger

from assets.assets import check_session
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
about_page = Blueprint('about_page', __name__)


class About:

    def __init__(self):
        pass

    @staticmethod
    def render_page(session):
        logger.debug("rendering template: about_us.html")
        return render_template('about_us.html',
                               login=check_session(session),
                               current_url='/about'
                               )
