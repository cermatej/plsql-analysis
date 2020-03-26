from random import randint
from datetime import datetime

import connexion

from parser_api.models.api_response import ApiResponse  # noqa: E501
from parser_api.models.doc import Doc  # noqa: E501
from parser_api import util
from parser_api.parser.TokenExtractor import TokenExtractor
from elasticsearch import Elasticsearch


def add_doc(body):  # noqa: E501
    """Add query doc to Elasticsearch

     # noqa: E501

    :param body: PL/SQL document object that needs to be indexed
    :type body: dict | bytes

    :rtype: None
    """

    if connexion.request.is_json:
        body = Doc.from_dict(connexion.request.get_json())  # noqa: E501

    if (not body.body or not body.index):
        return ApiResponse(status='Invalid input', tokens=None), 405

    try:
        te = TokenExtractor()
        tokens = te.analyse(body.body)
    except:
        return ApiResponse(status='Error while parsing query', tokens=None), 500

    doc = {
        'query': body.body,
        'tokens': tokens,
        'exec_time': randint(20, 1000),
        'timestamp': datetime.now()
    }

    # todo return error message when cant connect to es
    es = Elasticsearch()

    es_index = f'plsql_{body.index}'

    # es.cluster.health(wait_for_status='yellow', request_timeout=1)
    es.indices.create(index=es_index, ignore=400)
    es.index(index=es_index, body=tokens)

    return ApiResponse(status='Created', tokens=tokens), 201
