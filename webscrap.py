#!/usr/bin/env python3
# (C) savsher@gmail.com 20171104

import os
import sys
import atexit
import signal
import time
import used-avtomir
import requests


def daemonize(pidfile, *, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    if os.path.exists(pidfile):
        raise RuntimeError('Already running')

    # First fork (detaches from parent)
    try:
        if os.fork() > 0:
            raise SystemExit(0)  # Parent exit
    except OSError as e:
        raise RuntimeError('fork #1 failed.')
    os.chdir(os.getcwd())
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
    """ Main function """
    urlData = set()
    baseData = set()
    newset = set()
    oldset = set()

    # Main circle
    print('Daemon <webscraping> started with pid {}\n'.format(os.getpid()))
    while True:
        urlData.clear()
        baseData.clear()
        newset.clear()
        oldset.clear()
        site = 'used-avtomir.ru'
        # Scrap data from site
        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                            ' Chrome/61.0.3163.79 Safari/537.36'})
            z = used-avtomir.get_all_site(s)
            print(z)
            for i in z:
                if i not in ['arh', 'vrn']:
                    continue
                if get_link(s, ''.join(('http://', i, '.', site), dict())):
                    #print('{} - get data from site'.format(time.ctime()))
                    z = check_dbs(url)
                    if z is not None:
                        #print('{} - get data from db and compare it with new'.format(time.ctime()))
                        send_emails(z, 'http://'+url)
                        #print('{} - send new data to email'.format(time.ctime()))
                    sys.stdout.flush()
            print('Get Data from sites {}'.format(url))
        # Coffee break
        time.sleep(30)



if __name__ == '__main__':
    cur_dir = os.getcwd()
    pid_file = cur_dir + '/webscrap.pid'
    log_file = cur_dir + '/webscrap.log'
    if len(sys.argv) != 2:
        print('Usage: {} [start|stop]'.format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)
    if sys.argv[1] == 'start':
        try:
            daemonize(pid_file, stdout=log_file, stderr=log_file)
        except RuntimeError as e:
            print(e, file=sys.stderr)
            raise SystemExit(1)
        # Main function
        web_scraping()

    elif sys.argv[1] == 'stop':
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                os.kill(int(f.read()), signal.SIGTERM)
        else:
            print('Not running', file=sys.stderr)
            raise SystemExit(1)
    else:
        print('Unknown command {!r}'.format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)