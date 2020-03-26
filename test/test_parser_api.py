import os
import parser_client
from parser_client import Configuration
from parser_client.rest import ApiException
from pprint import pprint
import pytest

from rest.parser_api.parser.TokenExtractor import TokenExtractor

@pytest.mark.parametrize(
    "query,result",
    [
        ('SELECT mycolumn FROM mytable',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'mycolumn'}}),
        ('SELECT id FROM users WHERE name = "DAVID"',
         {'type': 'select', 'tables': {'users'}, 'columns': {'id', 'name'}, 'values': {'DAVID'}}),
        ('select * from users',
         {'type': 'select', 'tables': {'users'}}),
        ('Select id FROM users; SELECT id2 FROM users2;',
         {'type': 'select', 'tables': {'users'}, 'columns': {'id'}}),
        ('SELECT column_name AS alias_name FROM users;',
         {'type': 'select', 'tables': {'users'}, 'columns': {'column_name'}, 'aliases': {'alias_name'}}),
        ('INSERT INTO films VALUES ("Bananas", 105, \'Comedy\');',
         {'type': 'insert', 'tables': {'films'}, 'values': {'Bananas', 'Comedy', '105'}}),
        ('SELECT tbl1.mycolumn FROM long_table_name tbl1;',
         {'type': 'select', 'tables': {'long_table_name'}, 'columns': {'tbl1.mycolumn'}, 'aliases': {'tbl1'}}),
        ('SELECT first, second as col2 FROM mytable tbl1;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'first', 'second'}, 'aliases': {'col2', 'tbl1'}}),
        ('SELECT col1 FROM mytable ORDER BY col2 DESC, col3 ASC;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'col1', 'col2', 'col3'}}),
        ('SELECT col1 FROM mytable ORDER BY col2 DESC, col3 ASC;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'col1', 'col2', 'col3'}}),
        ('SELECT col1 FROM mytable WHERE col2 > 100',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'col1', 'col2'}, 'values': {'100'}}),
        ('SELECT col1 FROM mytable JOIN anothertable ON mytable.col2 = anothertable.col3;',
         {'type': 'select', 'tables': {'mytable', 'anothertable'}, 'columns': {'col1', 'mytable.col2', 'anothertable.col3'}}),
        ('SELECT COUNT (customer_id) FROM customer GROUP BY store_id;',
         {'type': 'select', 'tables': {'customer'}, 'columns': {'customer_id', 'store_id'}, 'funcs': {'count'}}),
        ('SELECT SUM(column_1) FROM mytable GROUP BY column_1 HAVING col3 > 100;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'column_1', 'col3'}, 'funcs': {'sum'}, 'values': {'100'}}),
        ('select distinct name from t1;',
         {'type': 'select', 'tables': {'t1'}, 'columns': {'name'}, 'prefs': {'distinct'}}),
        ('select * from t2 left outer join t3 using(dummy)',
         {'type': 'select', 'tables': {'t2', 't3'}, 'columns': {'dummy'}}),

    ]
)
def test_analyse(query, result):
    te = TokenExtractor()
    tokens = te.analyse(query)

    # ignore metadata field when asserting
    tokens = {a: val for a, val in te.tokens.items() if a != 'metadata'}

    assert tokens == result

################ BULK TESTS FROM EXAMPLE FILES

QUERIES_PER_FILE = 5
BULK_SIZE = 10
BULK_INDEX = 3

def pytest_generate_tests(metafunc):
    if "q_sample" in metafunc.fixturenames:
        metafunc.parametrize("q_sample", __get_query_sample(BULK_INDEX, BULK_SIZE))
    if 'q_all' in metafunc.fixturenames:
        metafunc.parametrize("q_all", __get_queries())

def __get_query_sample(bulk_index, bulk_size):
    queries = __get_queries()

    return queries[bulk_index * bulk_size:(bulk_index + 1) * bulk_size]

def __get_queries():
    queries = list()
    for file in os.listdir("examples"):
        f = open(f"examples/{file}", "r")
        queries_raw = f.read().split(';')
        queries_clean = [' '.join(q.rstrip().replace("\n", " ").split()) for q in queries_raw]
        queries_ne = [q for q in queries_clean if q]

        queries = queries + queries_ne[:QUERIES_PER_FILE]
    return queries

def test_analyse_single():
    single_index = 7
    q = __get_query_sample(BULK_INDEX, BULK_SIZE)

    test_analyse_bulk(q[single_index])

def test_analyse_all(q_all):
    __test_query(q_all)

def test_analyse_bulk(q_sample):
    __test_query(q_sample)

def __test_query(query):
    print(f'\n\n{query}\n')

    # get API instance
    conf = Configuration()
    conf.host = 'http://localhost:8080'
    api_instance = parser_client.DefaultApi(parser_client.ApiClient(conf))

    # create Doc object
    doc = parser_client.Doc(index='custom_db', body=query)
    try:
        res = api_instance.add_doc(doc)
    except ApiException as e:
        assert False, f"Exception when calling DefaultApi->add_doc: {e}"

    pprint(res)

    # any tokens found
    if not res.tokens:
        assert False, 'Any tokens found'
    # tokens contain value other than string
    if not res.tokens['type']:
        assert False, 'Query type not found'
    for key, tokens in res.tokens.items():
        # wrong classification
        if not isinstance(key, str):
            assert False, f'Key for tokens: "{tokens}" contain value other than str'
        # wrong save
        for token in tokens:
            if not isinstance(token, str):
                assert False, f'Value for key "{key}" contains value other than str'

    assert True