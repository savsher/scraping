from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode, quote_plus, unquote_plus

from bs4 import BeautifulSoup

pages = set()




url = "http://vrn.used-avtomir.ru/buy/?"
val = [
    ('FILTER[MODEL]',''),
    ('FILTER[BRAND]',''),
    ('FILTER[PRICE][MIN]','0'),
    ('FILTER[PRICE][MAX]','0'),
    ('FILTER[YEAR][MIN]','1980'),
    ('FILTER[YEAR][MAX]','2017'),
    ('FILTER[MILEAGE][MIN]','0'),
    ('FILTER[MILEAGE][MAX]','0'),
    ('FILTER[TYPE][0]','new'),
    ('FILTER[REGION]','406'),
    ('FILTER[BODY]',''),
    ('FILTER[ENGINE_TYPE]',''),
    ('FILTER[TRANSMISSION]',''),
    ('FILTER[DRIVE]','0'),
    ('FILTER[COLOR]','0'),
    ('FILTER[CABIN]','0'),
    ('FILTER[DISKS]','0'),
    ('FILTER[CLIMATE]','0'),
    ('FILTER[AUDIO]','0'),
    ('FILTER[SEAT_HEATING]','0'),
    ('FILTER[PARKTRONICS]','0'),
    ('FILTER[HEADLIGHTS]','0')
]

fval = urlencode(val, doseq=True)
print(fval)




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


"""
http://vrn.used-avtomir.ru/buy/?FILTER[MODEL%5D=&FILTER[BRAND%5D=&FILTER[PRICE%5D[MIN%5D=0&FILTER[PRICE%5D[MAX%5D=0&FILTER[YEAR%5D[MIN%5D=1980&FILTER[YEAR%5D[MAX%5D=2017&FILTER[MILEAGE%5D[MIN%5D=0&FILTER[MILEAGE%5D[MAX%5D=300000&FILTER[TYPE%5D[0%5D=new&FILTER[REGION%5D=406&FILTER[BODY_TYPE%5D=&FILTER[ENGINE_TYPE%5D=&FILTER[TRANSMISSION%5D=&FILTER[DRIVE%5D=0&FILTER[COLOR%5D=0&FILTER[CABIN%5D=0&FILTER[DISKS%5D=0&FILTER[CLIMATE%5D=0&FILTER[AUDIO%5D=0&FILTER[SEAT_HEATING%5D=0&FILTER[PARKTRONICS%5D=0&FILTER[HEADLIGHTS%5D=0
"""



if __name__ == '__main__':
    #url = "http://used-avtomir.ru/buy/new/"
    print(url+fval)
    html = urlopen(url+ fval)
    bsObj = BeautifulSoup(html.read())
    #data = bsObj.find_all("", {"class":"catalogue blocks"})
    data = bsObj.find("ul", {"class":"catalogue blocks"})
    for i in data.find_all("li"):
        print(i.find("a").attrs["href"])