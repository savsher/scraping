#
# (C) savsher@gmail.com 20171022
#

import requests
import re
from bs4 import BeautifulSoup

def get_html(s, page):
    """wget www"""
    dopant = "/buy/new/"
    if page is None:
        html = s.get(url+dopant)
    else:
        payload = page
        html = s.get(url+dapant, params=payload)
    html = s.get(url+dopant)
    bsObj = BeautifulSoup(html.text)
    data = bsObj.find("div", {"class": "catalogueContainer"})
    if data is None:
        return None
    return data

def get_ref(bsObj):
    global data
    refList = list()
    tmp = bsObj.find("ul", {"class": "catalogue blocks"})
    if tmp is None:
        return False
    for i in tmp.find_all("li"):
        data.add(i.find("a").attrs["href"])
    return True

def get_next_page(bsObj):
    tmp = bsObj.find("div", {"class": "pagination"})
    if tmp is None:
        return None
    else:
        next_ref = tmp.find("a", {"id": "_next_page"})
        if next_ref is None:
            return None
        else:
            x = re.split(r'=', re.split(r'\?', next_ref.attrs["href"] )[1])
            return {x[0]:x[1]}

if __name__ == '__main__':

    data = set()

    url = "http://vrn.used-avtomir.ru"
    with requests.Session() as s:
        s.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/61.0.3163.79 Safari/537.36'})
        heap = get_html(s, None)

        if heap is not None:
            get_ref(heap)
            payload = get_next_page(heap)
            heap = get_html(s, payload)
            if heap is not None:
                get_ref(heap)
                print(data)



    #html = s.get(url, params=payload)

