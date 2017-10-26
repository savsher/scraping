#
# (C) savsher@gmail.com 20171025
#

import requests
from bs4 import BeautifulSoup
import re

def get_source(s, page):
    annex = "/buy/new/"
    if page eq '1':
        html = s.get(url+annex)
    else:
        html = s.get(url+annex, params=page)
    bsObj = BeautifulSoup(html.text)
    data = bsObj.find("div", {"class": "catalogueContainer"})
    return data

def get_data(data):
    global urlData
    tmp = data.find("ul", {"class": "catalogue blocks"})
    if tmp is None:
        return False
    for x in tmp.find_all("li"):
        urlData.add(x.find("a").attrs["href"])
    return True

def get_page(data):
    tmp = data.find("div", {"class": "pagination"})
    if tmp is not None:
        next_ref = tmp.find("a", {"id": "_next_page"})
        if next_ref is not None:
            tmp = re.split(r'=', re.split(r'\?', next_ref.attrs["href"])[1])
            return({tmp[0]:tmp[1]})
    return None

if __name__ == '__main__':

    url = "http://vrn.used-avtomir.ru"
    urlData = set()

    with requests.Session() as s:
        s.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'})
        page = '1'
        while True:
            my = get_source(s, page)
            if html is not None:
