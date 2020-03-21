import connexion
import six
import json

from parser_api.models.api_response import ApiResponse  # noqa: E501
from parser_api.models.doc import Doc  # noqa: E501
from parser_api import util

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

    # todo check if request is valid
    # todo handle errors when parsing

    te = TokenExtractor()
    tokens = te.analyse(body.body)

    # todo save to elasticsearch
    res = ApiResponse(status='Created', tokens=tokens)

    return res, 201
    return 'Error while parsing query', 500
    return 'Invalid input', 405
