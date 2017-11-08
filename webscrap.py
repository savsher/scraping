#!/usr/bin/env python3
# (C) savsher@gmail.com 20171104

import os
import sys
import atexit
import signal
import time
import requests
from bs4 import BeautifulSoup
import re
import os
import sqlite3
import smtplib
import email.utils
from email.mime.text import MIMEText

def daemonize(pidfile, *, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    if os.path.exists(pidfile):
        raise RuntimeError('Already running')

    # First fork (detaches from parent)
    try:
        if os.fork() > 0:
            raise SystemExit(0)  # Parent exit
    except OSError as e:
        raise RuntimeError('fork #1 failed.')
    os.chdir('/')
    os.umask(0)
    os.setsid()

    # Second fork (relinquish session leadership)
    try:
        if os.fork() > 0:
            raise SystemExit(0)
    except OSError as e:
        raise RuntimeError('fork #2 failed')

    # Flush I/O buffers
    sys.stdout.flush()
    sys.stderr.flush()
    # Replace file descriptors for stdin, stdout, stderr
    with open(stdin, 'rb', 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(stdout, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open(stderr, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stderr.fileno())
    # Write the PID file
    with open(pidfile, 'w') as f:
        print(os.getpid(), file=f)
    # Arrange to have the PID file removed on exit/signal
    atexit.register(lambda : os.remove(pidfile))
    # Signal handler for termination (required)
    def sigterm_handler(signo, frame):
        raise SystemExit(1)
    signal.signal(signal.SIGTERM, sigterm_handler)

def web_scraping():
    url = "http://vrn.used-avtomir.ru"
    urlData = set()
    baseData = set()
    newset = set()
    oldset = set()

    def get_links(s, page):
        annex = "/buy/new/"
        if bool(page):
            html = s.get(url + annex, params=page)
        else:
            html = s.get(url + annex)
        bsObj = BeautifulSoup(html.text)
        data = bsObj.find("div", {"class": "catalogueContainer"})
        if data is None:
            return False
        tmp = data.find("ul", {"class": "catalogue blocks"})
        if tmp is None:
            return False
        for x in tmp.find_all("li"):
            urlData.add((x.a.find('div', {'class': 'caption'}).text,
                         x.a.find('div', {'class': 'price'}).text,
                         x.a.find('div', {'class': 'price'}).next_sibling.strip(),
                         x.a.attrs["href"]))

        tmp = data.find("div", {"class": "pagination"})
        if tmp is not None:
            nextref = tmp.find("a", {"id": "_next_page"})
            if nextref is not None:
                x = re.split(r'=', re.split(r'\?', nextref.attrs["href"])[1])
                get_links(s, {x[0]: x[1]})
            return True
        else:
            return True

    def check_dbs():
        """ Check db and get data from it """
        db_file = '/tmp/auto.db'
        schema_file = '/home/mrx/Pyfiles/scraping/auto_schema.sql'
        db_is_new = not os.path.exists(db_file)
        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()
            if db_is_new:
                sys.stdout.write('Create table')
                with open(schema_file, 'rt') as f:
                    schema = f.read()
                    conn.executescript(schema)
                    print('Insert data')
                    #cur.executemany('insert into usedavtomirru (name, price, description, link) values (?,?,?,?)', urlData)
                    #conn.commit()

            else:
                #print('Pull out data')
                cur.execute('select name, price, description, link from usedavtomirru')
                for row in cur.fetchall():
                    t1, t2, t3, t4 = row
                    baseData.add((t1, t2, t3, t4))

            oldset = baseData.difference(urlData)
            newset = urlData.difference(baseData)
            if oldset:
                cur.executemany('delete from usedavtomirru where name=? and price=? and description=? and link=?', oldset)
            if newset:
                cur.executemany('insert into usedavtomirru (name, price, description, link) values (?,?,?,?)', newset)
            cur.close()
            if newset:
                return newset
            else:
                return None

    def send_emails(newset):
        # Initial parameter for email
        mail_server = 'smtp.yandex.ru'
        mail_port = 465
        from_email = 'savpod@yandex.ru'
        to_email = 'savsher@gmail.com'
        to_email2 = 'savsher@yandex.ru'
        username = 'savpod'
        passwd = ',tutvjnf40'

        # Create the message
        newlist = []
        for i in newset:
            newlist.append(i[0] + '\n')
            newlist.append(i[1] + '\n')
            newlist.append(i[2] + '\n')
            newlist.append(url + i[3] + '\n')
            newlist.append('+++++++++++++++++++++++++++\n\n')

        msg = MIMEText(''.join(newlist))
        msg.set_unixfrom('author')
        msg['To'] = email.utils.formataddr(('Recipient', to_email))
        msg['From'] = email.utils.formataddr(('Author', from_email))
        msg['Subject'] = 'new objects'

        server = smtplib.SMTP_SSL(mail_server)
        try:
            # server.set_debuglevel(True)
            server.ehlo()
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()
            if server.has_extn('AUTH'):
                server.login(username, passwd)
                server.sendmail(from_email, [to_email, ], msg.as_string())
        finally:
            server.quit()

    print('Daemon <webscraping> started with pid {}\n'.format(os.getpid()))
    while True:
        urlData.clear()
        baseData.clear()
        newset.clear()
        oldset.clear()
        # Scrap data from site
        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                            ' Chrome/61.0.3163.79 Safari/537.36'})
            page = dict()
            if get_links(s, page):
                urlData.pop()
                urlData.pop()
                print('{} - get data from site'.format(time.ctime()))
                z = check_dbs()
                if z is not None:
                    print('{} - get data from db and compare it with new'.format(time.ctime()))
                    send_emails(z)
                    print('{} - print new data to email'.format(time.ctime()))
                sys.stdout.flush()
        # Coffee break
        time.sleep(6)

if __name__ == '__main__':
    PIDFILE = '/tmp/webscrap.pid'
    if len(sys.argv) != 2:
        print('Usage: {} [start|stop]'.format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)
    if sys.argv[1] == 'start':
        try:
            daemonize(PIDFILE, stdout='/tmp/webscrap.log', stderr='/tmp/webscrap.log')
        except RuntimeError as e:
            print(e, file=sys.stderr)
            raise SystemExit(1)
        # Main function
        web_scraping()

    elif sys.argv[1] == 'stop':
        if os.path.exists(PIDFILE):
            with open(PIDFILE) as f:
                os.kill(int(f.read()), signal.SIGTERM)
        else:
            print('Not running', file=sys.stderr)
            raise SystemExit(1)
    else:
        print('Unknown command {!r}'.format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)