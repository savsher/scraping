#!/usr/bin/env python3
# (C) savsher@gmail.com 20171104

import os
import sys
import atexit
import signal
import time
import usedavtomir
import requests
import configparser
import smtplib
import email.utils
from email.mime.text import MIMEText

# initial data
mflag = True

config = configparser.ConfigParser()
config.read('webscrap.ini')
mail_server = config.get('EMAIL', 'server')
from_email = config.get('EMAIL', 'from')
to_email = config.get('EMAIL', 'to')
to_email2 = config.get('EMAIL', 'to2')
username = config.get('EMAIL', 'user')
passwd = config.get('EMAIL', 'passwd')

if from_email == 'test@yandex.ru':
    mflag = False

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

def send_emails(newset, url):
    # Create the message
    newlist = []
    for i in newset:
        newlist.append(i[0] + '\n')
        newlist.append(i[1] + '\n')
        newlist.append(i[2] + '\n')
        newlist.append(url + i[3] + '\n')
        newlist.append('\n+++++++++++++++++++++++++++\n')

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
            server.sendmail(from_email, [to_email, to_email2 ], msg.as_string())
    finally:
        server.quit()

def web_scraping():
    """ Main function """

    # Main circle
    print('Daemon <webscraping> started with pid {}\n'.format(os.getpid()))

    while True:
        # Scrap data from site
        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                            ' Chrome/61.0.3163.79 Safari/537.36'})
            town = usedavtomir.get_all_avtomir(s)
            print(town)
            for i in town:
                if i not in ['arh', 'vrn', 'kr']:
                    continue
                usedavtomir.urlData.clear()
                usedavtomir.dbData.clear()
                if usedavtomir.get_link(s, ''.join(('http://', i, '.', usedavtomir.site)), dict()):
                    z = usedavtomir.check_db(''.join((i, '.', usedavtomir.site)))
                    if z is not None:
                        if mflag:
                            send_emails(z, ''.join(('http://', i, '.', usedavtomir.site)))
                        else:
                            print(''.join((i,'.', usedavtomir.site,':')))
                            print(z)
                    sys.stdout.flush()
        # Coffee break
        time.sleep(60)

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