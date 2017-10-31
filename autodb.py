#!/urs/bin/evn python3
# (C) savsher@gmail.com
# -*- coding: utf-8 -*-

import sqlite3
import os

db_file = 'webauto.db'
schema_file = 'webauto.sql'
myset() = set(
    ('Volkswagen Polo 2013', '520 000 руб.', '92482 км, 1.6 л., АКПП', '/buy/dealer/479/detail/62891/'),
    ('Volkswagen Amarok 2016', '2 300 000 руб.', '2355 км, 2 л., АКПП', '/buy/dealer/479/detail/62446/'))


def get_dbdata(conn, mydata):
    conn.executescript()
    pass

def wrt_dbdata(conn, mydata):
    insert into
    pass

def check_db(db_file='webauto.db', schema_file='webauto.sql'):
    db_is_new  = not os.path.exists(db_file)
    with sqlite3.connect(db_file) as conn:
        if db_is_new:
            print('Creating schema'):
            with open(schema_file, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            conn.executescript("""
            insert into 
            """)

if __name__ == '__main__':
    check_db()
    pass
