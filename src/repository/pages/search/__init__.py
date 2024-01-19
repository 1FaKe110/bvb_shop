import json

from flask import render_template, request, Blueprint, jsonify
from loguru import logger

from assets.assets import check_session
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
search_page = Blueprint('search_page', __name__)


class Search:

    def __init__(self):
        pass

    @staticmethod
    def get_search_page(session, es):
        user_request = request.args.get('q')
        if not user_request:
            return jsonify(dict(code='error', message='Missing search term'))

        # Поиск в ElasticSearch продуктов
        res = es.search(index="products-index",
                        body={"query": {
                            "match": {
                                "name": {
                                    "query": user_request.lower(),
                                    "boost": 1.0,
                                    "fuzziness": "2"
                                }}}})
        products = [row['_source'] for row in res['hits']['hits']]

        # Поиск в ElasticSearch категорий
        res = es.search(index="categories-index",
                        body={"query": {
                            "match": {
                                "c_name": {
                                    "query": user_request.lower(),
                                    "boost": 1.0,
                                    "fuzziness": "2"
                                }}}})
        categories = [row['_source'] for row in res['hits']['hits']]

        logger.info("Результаты запроса в бд [Products]")
        logger.info(json.dumps(products, indent=2, ensure_ascii=False))

        logger.info("Результаты запроса в бд [Categories]")
        logger.info(json.dumps(categories, indent=2, ensure_ascii=False))

        return render_template('search.html',
                               products=products,
                               categories=categories,
                               user_request=user_request,
                               session=check_session(session))

    @staticmethod
    def get_annotations(es):
        user_request = request.args.get('q')

        # Поиск в ElasticSearch категорий
        res = es.search(index="categories-index",
                        body={"query": {
                            "match": {
                                "c_name": {
                                    "query": user_request.lower(),
                                    "boost": 1.0,
                                    "fuzziness": "1"
                                }}}})

        categories = [row['_source'] for row in res['hits']['hits']][:5]
        return jsonify(categories)
