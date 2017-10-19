from urllib.request import urlopen

url = "https://stock.inchcape.ru"

if __name__ == '__main__':
    html = urlopen(url)
    with open('test.html', 'w') as output_file:
        output_file.write(html.encode('cp1251'))