import testtest
import sqlite3

myfun

db_file = 'home.db'
table_name = 't1_t2_test'
newset = set()
newset.add(('zzz',))
newset.add(('aaa',))
print(newset)
xxx = 'ttttt'

with sqlite3.connect(db_file) as conn:
    cur = conn.cursor()
    # Create table if not exists
    query = 'create table if not exists '+table_name+' ( id integer primary key autoincrement not null, name text)'
    try:
        cur.execute(query)
    except sqlite3.OperationalError as e:
        print('CREATE TABLE Error:\n{}'.format(e))

    #query = 'insert into '+table_name+' (name) values (?)'
    #try:
    #    cur.executemany(query, newset )
    #except sqlite3.OperationalError as e:
    #    print('INSERT Error:\n{}'.format(e))

    mmm = 't1'

    query = "select name from sqlite_master where type='table' and name='" + mmm + "'"
    try:
        cur.execute(query)
    except sqlite3.OperationalError as e:
        print('CREATE TABLE Error:\n{}'.format(e))
    if cur.fetchone() is None:
        print(False)


    cur.close()