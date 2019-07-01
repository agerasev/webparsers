import os
from urllib.request import urlopen
from html.parser import HTMLParser

import book


class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = {k: v for k, v in attrs}

        if "href" in attrs and attrs["href"].startswith("/books/"):
            self.links.append(attrs["href"])

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

def scan(url):
    base_url = "https://www.culture.ru"

    full_url = base_url + url
    print("scanning author '%s' ..." % full_url)

    res = urlopen(full_url)
    name = res.geturl().split("/")[-1]
    print("name: %s" % name)

    path = "./books/%s" % name
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    html = res.read().decode("utf-8")
    
    parser = Parser()
    parser.feed(html)

    for link in parser.links:
        book.download(link, path)

if __name__ == "__main__":
    scan("https://www.culture.ru/persons/8209")
