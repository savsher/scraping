#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import os
from contextlib import closing

# Initial data
site = 'used-avtomir.ru'
db_file = 'auto.db'
urlData = set()
dbData = set()

def get_all_avtomir(s):
    subsite = set()
    try:
        html = s.get('http://' + site, timeout=(3, 2))
    except requests.exceptions.RequestException as e:
        print('{}'.format(e))
        return subsite
    bsObj = BeautifulSoup(html.text)
    data = bsObj.find("select", {"id": "citySelect", "name": "CHANGED_REGION"})
    if data is not None:
        for x in data.find_all("option"):
            subsite.add(x.attrs["value"])
    return subsite

def get_link(s, url, page):
    """ Get Date from site"""
    """
    Get Data from site
    fill urlBase set
    :return True/False
    """
    annex = "/buy/new/"
    try:
        if bool(page):
            html = s.get(url + annex, params=page, timeout=(5, 2))
        else:
            html = s.get(url + annex, timeout=(5, 2))
    except requests.exceptions.RequestException as e:
        print('{}'.format(e))
        return False

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
            get_link(s, url, {x[0]: x[1]})
    return True

def check_db(url):
    """
    Check db and get data from it
    fill baseData
    :return set()/None
    """
    table_name = re.sub('[\-\.\/]' ,'', url)
    db_is_new = not os.path.exists(db_file)

    with sqlite3.connect(db_file) as conn:
        with closing(conn.cursor()) as cur:
            if db_is_new:
                # Create table
                query = 'create table ' + table_name + ' ( id integer primary key autoincrement not null, name text, price text, description text, link text)'
                try:
                    cur.execute(query)
                except sqlite3.OperationalError as e:
                    print('CREATE TABLE ERROR:\n{}'.format(e))
                    return None
                print('CREATE TABLE : {}'.format(table_name))
                # Fill table
                query = 'insert into ' + table_name + ' (name, price, description, link) values (?,?,?,?)'
                try:
                    cur.executemany(query, urlData)
                    conn.commit()
                except sqlite3.OperationalError as e:
                    print('INSERT INTO {} ERROR:\n{}'.format(table_name,e))
                    return None
                return None
            else:
                # Check table exit?
                query = "select name from sqlite_master where type='table' and name='"+table_name+"'"
                try:
                    cur.execute(query)
                    flag = cur.fetchone()
                except sqlite3.OperationalError as e:
                    print('SELECT NAME FROM SQLITE_MASTER ERROR:\n{}'.format(e))
                    return None
                if flag is None:
                    # Create table
                    query = 'create table ' + table_name + ' ( id integer primary key autoincrement not null, name text, price text, description text, link text)'
                    try:
                        cur.execute(query)
                        conn.commit()
                    except sqlite3.OperationalError as e:
                        print('CREATE TABLE ERROR:\n{}'.format(e))
                        return None
                    print('CREATE TABLE : {}'.format(table_name))
                    # Fill table
                    query = 'insert into ' + table_name + ' (name, price, description, link) values (?,?,?,?)'
                    try:
                        cur.executemany(query, urlData)
                        conn.commit()
                    except sqlite3.OperationalError as e:
                        print('INSERT INTO {} ERROR:\n{}'.format(table_name, e))
                        return None
                    return None
                else:
                    # Get Data from table
                    query = 'select name, price, description, link from ' + table_name
                    try:
                        cur.execute(query)
                        for row in cur.fetchall():
                            dbData.add(row)
                    except sqlite3.OperationalError as e:
                        print('SELECT {} ERROR:\n{}'.format(table_name, e))
                        return None
                    # Compare two set urlData and
                    old_set = dbData.difference(urlData)
                    new_set = urlData.difference(dbData)
                    #print('OLD: {}'.format(old_set))
                    #print('NEW: {}'.format(new_set))
                    if old_set:
                        query = 'delete from ' + table_name + ' where name=? and price=? and description=? and link=?'
                        try:
                            cur.executemany(query, old_set)
                            conn.commit()
                        except sqlite3.OperationalError as e:
                            print('DELETE FROM {} ERROR:\n{}'.format(table_name, e))
                            return None
                    if new_set:
                        query = 'insert into ' + table_name + '(name, price, description, link) values (?,?,?,?)'
                        try :
                            cur.executemany(query, new_set)
                            conn.commit()
                        except sqlite3.OperationalError as e:
                            print('INSERT INTO {} ERROR:\n{}'.format(table_name, e))
                            return None
                        return new_set
                    return None

if __name__ == '__main__':
    with requests.Session() as s:
        s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                        ' Chrome/61.0.3163.79 Safari/537.36'})
        for i in get_all_avtomir(s):
            if i not in ['arh','vrn','msk','kr']:
                continue
            urlData.clear()
            dbData.clear()
            if get_link(s, ''.join(('http://', i, '.', site)), dict()):
                z = check_db(''.join((i,'.', site)))
                if z is not None:
                    print(''.join(i, '.', site))
                    print(z)