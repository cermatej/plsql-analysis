import os
from pprint import pprint

from TokenExtractor import TokenExtractor
import pytest

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
         {'type': 'select', 'tables': {'customer'}, 'columns': {'customer_id', 'store_id'}, 'funcs': {'COUNT'}}),
        ('SELECT SUM(column_1) FROM mytable GROUP BY column_1 HAVING col3 > 100;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'column_1', 'col3'}, 'funcs': {'SUM'}, 'values': {'100'}})
    ]
)
def test_analyse(query, result):
    te = TokenExtractor()
    te.analyse(query)

    # ignore metadata field when asserting
    tokens = {a: val for a, val in te.tokens.items() if a != 'metadata'}

    assert tokens == result

################ BULK TESTS FROM EXAMPLE FILES

BULK_SIZE = 10
QUERIES_PER_FILE = 3
BULK_INDEX = 0

def pytest_generate_tests(metafunc):
    if "q" in metafunc.fixturenames:
        metafunc.parametrize("q", get_query_examples(BULK_INDEX, BULK_SIZE, QUERIES_PER_FILE))

def get_query_examples(bulk_group, bulk_size, queries_per_file):
    queries = list()
    for file in os.listdir("examples"):
        f = open(f"examples/{file}", "r")
        queries_raw = f.read().split(';')[:queries_per_file]
        queries = queries + [' '.join(q.rstrip().replace("\n", " ").split()) for q in queries_raw if q]

    return queries[bulk_group*bulk_size:(bulk_group+1)*bulk_size]

def test_analyse_single():
    single_index = 9
    q = get_query_examples(BULK_INDEX, BULK_SIZE, QUERIES_PER_FILE)

    test_analyse_bulk(q[single_index])

def test_analyse_bulk(q):
    print(f'\n\n{q}\n')
    # try:
    te = TokenExtractor()
    te.analyse(q)
    # except:
    #
    #     assert True # ignore

    pprint(te.tokens)

    if not te.tokens:
        assert False

    if None in te.tokens.keys():
        assert False

    assert True