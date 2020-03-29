import json
import logging

import requests
from elasticsearch import Elasticsearch
import sys

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ElasticInstance(metaclass=Singleton):

    HOST = 'elk'
    PORT_KIBANA = '5601'
    PORT_ES = '9200'
    OBJECTS_FILENAME = 'saved_objects.ndjson'
    REQUEST_HEADERS = {'kbn-xsrf': 'reporting'}
    TEMPLATE_NAME = 'plsql_template'

    def __init__(self):
        self.es = Elasticsearch(
            self.HOST
        )
        self.es_index_prefix = 'plsql_'

        logging.info('Waiting for ES status to turn yellow')
        self.es.cluster.health(wait_for_status='yellow', request_timeout=60)

    def index_doc(self, index, doc):
        es_index = self.es_index_prefix + index

        # create index if does not exist
        self.es.indices.create(index=es_index, ignore=400)
        return self.es.index(index=es_index, body=doc)

    def load_es_defaults(self):
        self.__load_index_patterns()
        self.__load_saved_objects()

    def __load_saved_objects(self):
        logging.info('Loading saved objects to Kibana')

        url = f"http://{self.HOST}:{self.PORT_KIBANA}/api/saved_objects/_import"
        files = {
            'file': open(self.OBJECTS_FILENAME, 'r')
        }
        response = requests.request("POST", url, headers=self.REQUEST_HEADERS, files=files)
        logging.debug(response.text)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f'Populating saved objects failed with error: {e}')
            sys.exit(1)

    def __load_index_patterns(self):
        logging.info('Loading index templates to Elasticsearch')

        try:
            template_body = json.load(open('index_template.json', 'r'))
            res = self.es.indices.put_template(self.TEMPLATE_NAME, template_body)
            logging.debug(res)
        except:
            print('Loading index templates failed with error')
            sys.exit(1)



