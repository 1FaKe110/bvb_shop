from flask import render_template, Blueprint
from loguru import logger

from assets.assets import check_session
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
delivery_page = Blueprint('delivery_page', __name__)


class Delivery:

    def __init__(self):
        pass

    @staticmethod
    def render_page(session):
        logger.debug("rendering template: delivery.html")
        return render_template('delivery.html',
                               current_url='/delivery',
                               login=check_session(session))
