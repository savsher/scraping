from bs4 import BeautifulSoup

import requests

s = requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/61.0.3163.79 Safari/537.36'})


def load_pages()


def getLinks(addition):
    print(url)
    html = requests.get(url+addition)
    bsObj = BeautifulSoup(html.text)
    data = bsObj.find("div", {"class": "catalogueContainer"})
    x = data.find("ul", {"class": "catalogue blocks"})
    for i in x.find_all("li"):
        print(i.find("a").attrs["href"])

    y = data.find("div", {"class": "pagination"})
    if y is None:
        return None
    else:
        next_ref = y.find("a", {"id": "_next_page"})
        if next_ref is None:
            return None
        else:
            return (next_ref.attrs["href"])


if __name__ == '__main__':

    url = "http://vrn.used-avtomir.ru/buy/new/"
    s = requests.Session()
    s.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'})
    html = s.get(url)
    bsObj = BeautifulSoup(html.text)
    data = bsObj.find("div", {"class": "catalogueContainer"})
    print(data)

    payload = {'PAGEN_1':'2'}
    html = s.get(url, params=payload)
    bsObj = BeautifulSoup(html.text)
    data = bsObj.find("div", {"class": "catalogueContainer"})
    y = data.find("div", {"class": "pagination"})
    next_ref = y.find("a", {"id": "_next_page"})
    if next_ref is None:
        print("asdfasdfadsf")
    else:
        print(next_ref)