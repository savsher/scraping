#
# (C) savsher@gmail.com 20171025
#

import requests
from bs4 import BeautifulSoup
import re
import os

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
    urlData = set()

    with requests.Session() as s:
        s.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                       ' Chrome/61.0.3163.79 Safari/537.36'})
        page = dict()
        if get_links(s, page):
            print(urlData)


