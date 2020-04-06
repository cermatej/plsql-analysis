import os
from elasticsearch import Elasticsearch
from parser_client import Configuration
import parser_client
from parser_client.rest import ApiException
from pprint import pprint
import pytest
import asyncio
from datetime import datetime
import pickle

from rest.parser_api.parser.TokenExtractor import TokenExtractor

QUERIES_PER_FILE = 5
BULK_SIZE = 10
BULK_INDEX = 3

INDEX_NAME = 'custom_db'
API_HOST = 'http://localhost:8080'

###################### PARSER TESTS #############################


@pytest.mark.parametrize(
    "query,result",
    [
        ('SELECT mycolumn FROM mytable',
         {'type': 'select', 'tables': ['mytable'], 'columns': ['mycolumn']}),
        ('SELECT id FROM users WHERE name = "DAVID"',
         {'type': 'select', 'tables': ['users'], 'columns': ['id', 'name'], 'values': ['DAVID']}),
        ('select * from users',
         {'type': 'select', 'tables': ['users']}),
        ('Select id FROM users; SELECT id2 FROM users2;',
         {'type': 'select', 'tables': ['users'], 'columns': ['id']}),
        ('SELECT column_name AS alias_name FROM users;',
         {'type': 'select', 'tables': ['users'], 'columns': ['column_name'], 'aliases': ['alias_name']}),
        ('INSERT INTO films VALUES ("Bananas", 105, \'Comedy\');',
         {'type': 'insert', 'tables': ['films'], 'values': ['Bananas', 'Comedy', '105']}),
        ('SELECT tbl1.mycolumn FROM long_table_name tbl1;',
         {'type': 'select', 'tables': ['long_table_name'], 'columns': ['tbl1.mycolumn'], 'aliases': ['tbl1']}),
        ('SELECT first, second as col2 FROM mytable tbl1;',
         {'type': 'select', 'tables': ['mytable'], 'columns': ['first', 'second'], 'aliases': ['col2', 'tbl1']}),
        ('SELECT col1 FROM mytable ORDER BY col2 DESC, col3 ASC;',
         {'type': 'select', 'tables': ['mytable'], 'columns': ['col1', 'col2', 'col3']}),
        ('SELECT col1 FROM mytable ORDER BY col2 DESC, col3 ASC;',
         {'type': 'select', 'tables': ['mytable'], 'columns': ['col1', 'col2', 'col3']}),
        ('SELECT col1 FROM mytable WHERE col2 > 100',
         {'type': 'select', 'tables': ['mytable'], 'columns': ['col1', 'col2'], 'values': ['100']}),
        ('SELECT col1 FROM mytable JOIN anothertable ON mytable.col2 = anothertable.col3;',
         {'type': 'select', 'tables': ['mytable', 'anothertable'], 'columns': ['col1', 'mytable.col2', 'anothertable.col3']}),
        ('SELECT COUNT (customer_id) FROM customer GROUP BY store_id;',
         {'type': 'select', 'tables': ['customer'], 'columns': ['customer_id', 'store_id'], 'funcs': ['count']}),
        ('SELECT SUM(column_1) FROM mytable GROUP BY column_1 HAVING col3 > 100;',
         {'type': 'select', 'tables': ['mytable'], 'columns': ['column_1', 'col3'], 'funcs': ['sum'], 'values': ['100']}),
        ('select distinct name from t1;',
         {'type': 'select', 'tables': ['t1'], 'columns': ['name'], 'prefs': ['distinct']}),
        ('select * from t2 left outer join t3 using(dummy)',
         {'type': 'select', 'tables': ['t2', 't3'], 'columns': ['dummy']}),
        ('DELETE FROM hr.locations@remote WHERE location_id > 3000;',
         {}),
    ]
)
def test_analyse(query, result):
    tok_res = __test_query_parser(query)

    # ignore metadata field when asserting
    tokens = {a: val for a, val in tok_res.items() if a != 'metadata'}
    assert tokens == result

def test_parser_analyse_all(q_all):
    __test_query_parser(q_all)

###################### API TESTS #############################

def test_api_analyse_all(q_all):
    """
    Test whole queries dataset
    :param q_all: whole dataset
    """
    __test_query_api(q_all)

###################### DATA #############################

def pytest_generate_tests(metafunc):
    if 'q_all' in metafunc.fixturenames:
        metafunc.parametrize("q_all", __get_queries())

def __get_queries():
    queries = list()
    for file in os.listdir("examples"):
        f = open(f"examples/{file}", "r")
        queries_raw = f.read().split(';')
        queries_clean = [' '.join(q.rstrip().replace("\n", " ").split()) for q in queries_raw]
        queries_ne = [q for q in queries_clean if q]

        queries = queries + queries_ne[:QUERIES_PER_FILE]
    # queries in pickle file
    return queries + pickle.load(open( "queries.p", "rb" ))

###################### ASYNC #############################

async def send_request(query):
    api_instance = __get_api_instance()

    return api_instance.add_doc(parser_client.Doc(index=INDEX_NAME, body=query))

async def send_requests(loop):
    queries = __get_queries()
    tasks = [loop.create_task(send_request(q)) for q in queries]
    print(f'Creating {len(queries)} objects')
    await asyncio.wait(tasks)
    return tasks

def test_api_all_async():
    """
    Push all available queries to API instance async and print summary
    """
    tick = datetime.now()

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(send_requests(loop))

    tock = datetime.now()
    seconds = round((tock - tick).total_seconds())

    created = 0
    for r in results:
        try:
            created = created + int(r.result().status == 'Created')
        except:
            continue

    print(f"Summary: created {created}/{len(results)} documents in {seconds} seconds")

###################### HELPER METHODS #############################

def __delete_existing_index():
    Elasticsearch().indices.delete(index=f'plsql_{INDEX_NAME}', ignore=404)

def __test_query_api(query):
    print(f'\n\n{query}\n')

    # get API instance
    api_instance = __get_api_instance()

    # create Doc object
    doc = parser_client.Doc(index=INDEX_NAME, body=query)
    try:
        res = api_instance.add_doc(doc)
    except ApiException as e:
        assert False, f"Exception when calling DefaultApi->add_doc: {e}"

    pprint(res)

    __assert_tokens(res.tokens)


def __assert_tokens(tokens):
    # any tokens found
    if not tokens:
        assert False, 'Any tokens found'
    # tokens contain value other than string
    if not tokens['type']:
        assert False, 'Query type not found'
    for key, t in tokens.items():
        # wrong classification
        if not isinstance(key, str):
            assert False, f'Key for tokens: "{t}" contain value other than str'
        # wrong save
        for token in t:
            if not isinstance(token, str):
                assert False, f'Value for key "{key}" contains value other than str'
    assert True


def __test_query_parser(query):
    te = TokenExtractor()
    tokens = te.analyse(query)

    __assert_tokens(tokens)
    return tokens

def __get_api_instance():
    conf = Configuration()
    conf.host = API_HOST
    api_instance = parser_client.DefaultApi(parser_client.ApiClient(conf))
    return api_instance