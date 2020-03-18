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

def pytest_generate_tests(metafunc):
    if "q" in metafunc.fixturenames:
        metafunc.parametrize("q", get_query_examples())

def get_query_examples():
    queries = list()
    for file in os.listdir("examples"):
        f = open(f"examples/{file}", "r")
        queries = queries + [s.rstrip().replace("\n", " ") for s in f.read().split(';')]

    return [s for s in queries[:10] if s]

def test_analyse_undefined(q):
    te = TokenExtractor()
    te.analyse(q)

    print(f'\n\n{q}\n\n')
    pprint(te.tokens)

    if None in te.tokens.keys():
        assert False

    assert True