from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

pages = set()

def getLinks(url):
    global pages
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bsObj = BeautifulSoup(html.read())
        data = bsObj.body.findAll("ul")
    except AttributeError as e:
        return None
    return data


if __name__ == '__main__':
    url = "http://used-avtomir.ru/buy/new/"
    html = urlopen(url)
    bsObj = BeautifulSoup(html.read())
    #data = bsObj.find_all("", {"class":"catalogue blocks"})
    data = bsObj.find("ul", {"class":"catalogue blocks"})
    for i in data.find_all("li"):
        print(i.find("a").attrs["href"])