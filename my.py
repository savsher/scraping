import testtest
import sqlite3

my = set()
my.add('1111')
my.clear()
if my:
    print('YES')
my.add('xxxxx')
if my:
    print('NO')