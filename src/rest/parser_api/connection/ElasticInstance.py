import json
import logging
import time

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

    HOST = 'http://elk'
    PORT_KIBANA = '5601'
    PORT_ES = '9200'
    OBJECTS_FILENAME = 'saved_objects.ndjson'
    REQUEST_HEADERS = {'kbn-xsrf': 'reporting'}
    TEMPLATE_NAME = 'plsql_template'

    ES_ENDPOINT = f"{HOST}:{PORT_ES}/_cluster/health"
    KIBANA_ENDPOINT = f"{HOST}:{PORT_KIBANA}"
    CONN_N_TRIES = 60

    def __init__(self):
        self.es = Elasticsearch(
            self.HOST
        )
        self.es_index_prefix = 'plsql_'

        self.__wait_for_ready(self.ES_ENDPOINT)
        self.__wait_for_ready(self.KIBANA_ENDPOINT)

    def __wait_for_ready(self, endpoint):
        for i in range(1,self.CONN_N_TRIES+1):
            try:
                logging.info(f'Waiting for API endpoint {endpoint} to be up ({i}/{self.CONN_N_TRIES})')
                res = requests.request("GET", endpoint, headers=self.REQUEST_HEADERS)
                if not res.status_code == 200:
                    raise ConnectionError
                return res
            except:
                time.sleep(2)
                logging.debug('Elasticsearch request failed!')

        logging.error(f'Could not connect to endpoint. Exiting...')
        sys.exit(1)

    def index_doc(self, index, doc):
        es_index = self.es_index_prefix + index

        return self.es.index(index=es_index, body=doc)

    def load_es_defaults(self):
        self.__load_index_patterns()
        self.__load_saved_objects()

    def __load_saved_objects(self):
        logging.info('Loading saved objects to Kibana')

        url = f"{self.KIBANA_ENDPOINT}/api/saved_objects/_import"
        files = {'file': open(self.OBJECTS_FILENAME, 'r')}
        response = requests.request("POST", url, headers=self.REQUEST_HEADERS, files=files)
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



