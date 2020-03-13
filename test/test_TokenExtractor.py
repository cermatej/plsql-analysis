import os
from TokenExtractor import TokenExtractor
import pytest


@pytest.mark.parametrize(
    "query,result",
    [
        ('SELECT mycolumn FROM mytable',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'mycolumn'}}),
        ('SELECT id FROM users WHERE name = "DAVID"',
         {'type': 'select', 'tables': {'users'}, 'columns': {'id', 'name'}}),
        ('select * from users',
         {'type': 'select', 'tables': {'users'}, 'columns': {'*'}}),
        ('Select id FROM users; SELECT id2 FROM users2;',
         {'type': 'select', 'tables': {'users'}, 'columns': {'id'}}),
        ('SELECT column_name AS alias_name FROM users;',
         {'type': 'select', 'tables': {'users'}, 'columns': {'column_name'}, 'aliases': {'alias_name'}}),
        ('INSERT INTO films VALUES ("UA502", "Bananas", 105, "1971-07-13", "Comedy", "82 minutes");',
         {'type': 'insert', 'tables': {'films'}}),
        ('SELECT tbl1.mycolumn FROM long_table_name tbl1;',
         {'type': 'select', 'tables': {'long_table_name'}, 'columns': {'tbl1.mycolumn'}, 'aliases': {'tbl1'}}),
        ('SELECT first, second as col2 FROM mytable tbl1;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'first', 'second'}, 'aliases': {'col2', 'tbl1'}}),
        ('SELECT col1 FROM mytable ORDER BY col2 DESC, col3 ASC;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'col1', 'col2', 'col3'}}),
        ('SELECT col1 FROM mytable ORDER BY col2 DESC, col3 ASC;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'col1', 'col2', 'col3'}}),
        ('SELECT col1 FROM mytable WHERE col2 > 100',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'col1', 'col2'}}),
        ('SELECT col1 FROM mytable JOIN anothertable ON mytable.col2 = anothertable.col3;',
         {'type': 'select', 'tables': {'mytable', 'anothertable'}, 'columns': {'col1', 'mytable.col2', 'anothertable.col3'}}),
        ('SELECT COUNT (customer_id) FROM customer GROUP BY store_id;',
         {'type': 'select', 'tables': {'customer'}, 'columns': {'customer_id', 'store_id'}, 'funcs': {'COUNT'}}),
        ('SELECT SUM(column_1) FROM mytable GROUP BY column_1 HAVING col3 > 100;',
         {'type': 'select', 'tables': {'mytable'}, 'columns': {'column_1', 'col3'}, 'funcs': {'SUM'}})

    ]
)
def test_analyse(query, result):
    te = TokenExtractor()
    te.analyse(query)

    assert te.tokens == result


def test_analyse_bulk():
    for file in os.listdir("examples"):
        f = open(f"examples/{file}", "r")
        queries_raw = f.read().split(';')
        queries = [s.rstrip() for s in queries_raw]

        for query in queries:
            te = TokenExtractor()
            te.analyse(query)

            print(query)
            print(te.tokens)

            assert True
