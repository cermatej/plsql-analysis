# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from parser_api.models.base_model_ import Model
from parser_api import util


class ApiResponse(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, status: str=None, tokens: object=None):  # noqa: E501
        """ApiResponse - a model defined in Swagger

        :param status: The status of this ApiResponse.  # noqa: E501
        :type status: str
        :param tokens: The tokens of this ApiResponse.  # noqa: E501
        :type tokens: object
        """
        self.swagger_types = {
            'status': str,
            'tokens': object
        }

        self.attribute_map = {
            'status': 'status',
            'tokens': 'tokens'
        }

        self._status = status
        self._tokens = tokens

    @classmethod
    def from_dict(cls, dikt) -> 'ApiResponse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ApiResponse of this ApiResponse.  # noqa: E501
        :rtype: ApiResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def status(self) -> str:
        """Gets the status of this ApiResponse.


        :return: The status of this ApiResponse.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status: str):
        """Sets the status of this ApiResponse.


        :param status: The status of this ApiResponse.
        :type status: str
        """

        self._status = status

    @property
    def tokens(self) -> object:
        """Gets the tokens of this ApiResponse.


        :return: The tokens of this ApiResponse.
        :rtype: object
        """
        return self._tokens

    @tokens.setter
    def tokens(self, tokens: object):
        """Sets the tokens of this ApiResponse.


        :param tokens: The tokens of this ApiResponse.
        :type tokens: object
        """

        self._tokens = tokens
