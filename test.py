#
# (C) savsher@gmail.com 20171025
#
import requests
from bs4 import BeautifulSoup
import re
import os
import sqlite3
import smtplib
import email.utils
from email.mime.text import MIMEText


def get_all_site(s):
    url = 'http://used-avtomir.ru'
    subsite = set()
    try:
        html = s.get(url, timeout=(3, 2))
    except requests.exceptions.RequestException as e:
        print('{}'.format(e))
        return subsite
    bsObj = BeautifulSoup(html.text)
    data = bsObj.find("select", {"id":"citySelect", "name":"CHANGED_REGION"})
    if data is not None:
        for x in data.find_all("option"):
            subsite.add(x.attrs["value"])
    return subsite

#import getpass
def get_links(s, page):
    global urlData
    annex = "/buy/new/"
    if bool(page):
        html = s.get(url+annex, params=page)
    else:
        html = s.get(url+annex)
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
            get_links(s, {x[0]:x[1]})
        return True
    else:
        return True

if __name__ == '__main__':
    url = "http://vrn.used-avtomir.ru"
    #url = "http://used-avtomir.ru"

    urlData = set()
    baseData = set()
    new_set = set()
    old_set = set()

    # Scrap data from site
    with requests.Session() as s:
        s.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                       ' Chrome/61.0.3163.79 Safari/537.36'})

        z = get_all_site(s)
        print(z)
        page = dict()
        if get_links(s, page):
            #urlData.pop()
            pass
            #print(urlData)

    # Work with database
    db_file = 'auto.db'
    schema_file = 'auto_schema.sql'
    db_is_new = not os.path.exists(db_file)
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        if db_is_new:
            print('Create schema')
            with open(schema_file, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            print('Insert data')
            cur.executemany('insert into usedavtomirru (name, price, description, link) values (?,?,?,?)', urlData)
            conn.commit()
        else:
            print('Pull out data')
            cur.execute('select name, price, description, link from usedavtomirru')
            for row in cur.fetchall():
                t1, t2, t3, t4 = row
                baseData.add((t1, t2, t3, t4))
            old_set = baseData.difference(urlData)
            new_set = urlData.difference(baseData)
            if old_set:
                cur.executemany('delete from usedavtomirru where name=? and price=? and description=? and link=?', old_set)
            if new_set:
                cur.executemany('insert into usedavtomirru (name, price, description, link) values (?,?,?,?)', new_set)
        cur.close()
    if new_set:
        print(new_set)

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
        for i in new_set:
            newlist.append(i[0]+'\n')
            newlist.append(i[1]+'\n')
            newlist.append(i[2]+'\n')
            newlist.append(url+i[3]+'\n')
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
                server.sendmail(from_email, [to_email,], msg.as_string())
        finally:
            server.quit()