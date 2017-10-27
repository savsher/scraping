import csv
m = set()
m.add(('sdfas','asdf'))
m.add(('a', 'b'))
m.add(('sdfz', 'zzzz', 'dddd', 'dddddd', 'ddd'))

with open('eggs.csv', 'w') as f:
    mywr = csv.writer(f, delimiter=' ')
    for i in m:
        mywr.writerow(i)