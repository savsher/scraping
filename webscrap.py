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

def main():
    sys.stdout.write('Daemon started with pid {}\n'.format(os.getpid()))
    while True:
        sys.stdout.write('Test {}\n'.format(time.ctime()))
        time.sleep(200)

def web_scraping():
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

    sys.stdout.write('Daemon <webscraping> started with pid {}\n'.format(os.getpid()))
    while True:
        url = "http://vrn.used-avtomir.ru"
        urlData = set()
        #baseData = set()
        # Scrap data from site
        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                            ' Chrome/61.0.3163.79 Safari/537.36'})
            page = dict()
            if get_links(s, page):
                # urlData.pop()
                sys.stdout.write('{} - get data from site'.format(time.clock()))
        # Coffee break
        time.sleep(20)

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