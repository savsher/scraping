import sqlite3

db_file = 'home.db'
table_name = 't1'
newset = set()
newset.add('zzz')
newset.add('aaa')
print(newset)

with sqlite3.connect(db_file) as conn:
    cur = conn.cursor()
    # Create table if not exists
    query = 'create table if not exists '+table_name+' ( id integer primary key autoincrement not null, name text)'
    try:
        cur.execute(query)
    except sqlite3.OperationalError as e:
        print('CREATE TABLE Error:\n{}'.format(e))

    query = 'insert into '+table_name+' (name) values (?)'
    try:
        cur.execute(query, 'zzz')
    except sqlite3.OperationalError as e:
        print('INSERT Error:\n{}'.format(e))
    cur.close()