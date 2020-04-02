import pickle
import requests
from bs4 import BeautifulSoup

URL_PREF = 'https://docs.oracle.com/cd/B28359_01/server.111/b28286/'
FILENAME = "queries.p"
RESERVED_WORDS = ["ACCESS", "ADD", "ALL", "ALTER", "ANY", "AS", "ASC", "AUDIT", "BETWEEN", "BY", "CHECK",
                  "CLUSTER", "COLUMN", "COMMENT", "COMPRESS", "CONNECT", "CREATE", "CURRENT", "DECIMAL",
                  "DEFAULT", "DELETE", "DESC", "DISTINCT", "DROP", "ELSE", "EXCLUSIVE", "EXISTS", "FILE", "FLOAT",
                  "FOR", "FROM", "GRANT", "GROUP", "HAVING", "IDENTIFIED", "IMMEDIATE", "IN", "INCREMENT", "INDEX",
                  "INITIAL", "INSERT", "INTEGER", "INTERSECT", "INTO", "IS", "LEVEL", "LIKE", "LOCK", "LONG",
                  "MAXEXTENTS", "MINUS", "MLSLABEL", "MODE", "MODIFY", "NOAUDIT", "NOCOMPRESS", "NOT", "NOWAIT", "NULL",
                  "OF", "OFFLINE", "ON", "ONLINE", "OPTION", "ORDER", "PCTFREE", "PRIOR", "PRIVILEGES",
                  "PUBLIC", "RAW", "RENAME", "RESOURCE", "REVOKE", "ROWNUM", "ROWS", "SELECT",
                  "SESSION", "SET", "SHARE", "SIZE", "SMALLINT", "START", "SUCCESSFUL", "SYNONYM", "SYSDATE", "TABLE",
                  "THEN", "TRIGGER", "UNION", "UNIQUE", "UPDATE", "USER", "VALIDATE", "VALUES", "VARCHAR",
                  "VARCHAR2", "VIEW", "WHENEVER", "WHERE", "WITH"]


def get_link(page):
    return f'{URL_PREF}/{page}'


def save():
    page = 'preface.htm'
    queries = []

    while True:
        soup = BeautifulSoup(requests.get(get_link(page)).content, 'html.parser')

        pres = soup.find_all('pre')
        q_list = [i.get_text() for i in soup.find_all('pre')]
        if q_list:
            # split by ; and remove trailing & leading quotes
            q_cleaned = []
            for q in q_list:
                for q_s in q.split(';'):
                    q_cleaned.append(' '.join(q_s.replace('\n', '').strip().strip('"\'').strip().split()))
            # filter using reserved words
            q_filtered = []
            for q in q_cleaned:
                for word in RESERVED_WORDS:
                    if q.find(word) != -1:
                        q_filtered.append(q)
                        break
            if q_list != q_filtered:
                print(f'Discarded {len(q_cleaned) - len(q_filtered)} values')
            queries = queries + q_filtered
        print(f'Queries found so far - {len(queries)} - {page}')

        next_link = soup.find("link", {"rel": "Next"})
        if not next_link:
            break

        page = next_link.attrs['href']

    pickle.dump(queries, open(FILENAME, "wb"))


if __name__ == '__main__':
    save()
