# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from parser_api.models.api_response import ApiResponse  # noqa: E501
from parser_api.models.doc import Doc  # noqa: E501
from parser_api.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_add_doc(self):
        """Test case for add_doc

        Add query doc to Elasticsearch
        """
        body = Doc()
        response = self.client.open(
            '/doc',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
