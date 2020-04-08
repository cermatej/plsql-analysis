#!/usr/bin/env python3
import logging.config
import os

import connexion
import yaml

from parser_api import encoder
from parser_api.connection.ElasticInstance import ElasticInstance

def setup_logging(
        default_path='logging.yaml',
        default_level=logging.INFO,
        env_key='LOG_CFG'
) -> None:
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def main():
    setup_logging()

    ei = ElasticInstance()
    ei.load_es_defaults()

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'PL/SQL analysis'})
    app.run(port=8080)

if __name__ == '__main__':
    main()
