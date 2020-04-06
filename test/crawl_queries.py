import pickle
import re

import requests
from bs4 import BeautifulSoup

URL_PREF = 'https://docs.oracle.com/cd/B28359_01/server.111/b28286/'
FILENAME = "queries.p"
RESERVED_WORDS = ["ACCESS", "ADD", "ALTER", "AUDIT", "CLUSTER", "COMMENT", "COMPRESS", "CONNECT", "CREATE", "CURRENT",
                  "DELETE", "DROP", "FOR", "GRANT", "INCREMENT", "INDEX",
                  "INITIAL", "INSERT", "INTERSECT", "INTO", "LOCK", "MODE", "MODIFY",
                  "PCTFREE",
                  "PUBLIC", "RENAME", "RESOURCE", "REVOKE", "SELECT",
                  "SESSION", "SET"
                             "TRIGGER", "UNION", "UPDATE", "VALIDATE"]


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
                    q_cleaned.append(' '.join(q_s.replace('\n', ' ').strip().strip('"\'/*').strip().split()))
            # remove empty strings and comments
            q_cleaned = [re.sub('/ ?\*.*\* ?/( \*)?', '', q) for q in q_cleaned if q]
            # filter using reserved words
            q_filtered = []
            for q in q_cleaned:
                for word in RESERVED_WORDS:
                    if q.startswith(word):
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
