#!/usr/bin/env python3

import connexion
import requests

from parser_api import encoder
from parser_api.connection.ElasticInstance import ElasticInstance


def main():
    ei = ElasticInstance()
    ei.populate_saved_objects()

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'PL/SQL analysis'})
    app.run(port=8080)

if __name__ == '__main__':
    main()
