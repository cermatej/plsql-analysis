from random import randint, random
from datetime import datetime

import connexion
from parser_api.connection.ElasticInstance import ElasticInstance

from parser_api.models.api_response import ApiResponse  # noqa: E501
from parser_api.models.doc import Doc  # noqa: E501
from parser_api.parser.TokenExtractor import TokenExtractor


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

    tick = datetime.now()
    try:
        te = TokenExtractor()
        tokens = te.analyse(body.body)
    except:
        return ApiResponse(status='Error while parsing query', tokens=None), 500
    tock = datetime.now()

    exec_time = ((len(body.body) / 100) * randint(100,
                                                  700)) if random() < 0.8 else None  # argument optional in api - mock for testing purposes
    doc = {
        'query': body.body,
        'tokens': tokens,
        'parse_time': int((tock - tick).total_seconds() * 1000),
        'exec_time': exec_time,  # optional parameter - None if not provided
        'timestamp': datetime.now()  # optional parameter - if not provided use datetime.now()
    }

    ei = ElasticInstance()
    res = ei.index_doc(body.index, doc)

    if res['result'] == 'created':
        return ApiResponse(status='Created', tokens=tokens), 201

    return ApiResponse(status='Undefined error', tokens=None), 500

    # todo return whole doc instead of tokens?
