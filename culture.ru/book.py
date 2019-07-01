import os
from urllib.request import urlopen
from html.parser import HTMLParser


class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.href = None
        self.link = None

    def handle_starttag(self, tag, attrs):
        attrs = {k: v for k, v in attrs}

        if tag == "a" and "class" in attrs and "button" in attrs["class"].split(" "):
            self.href = attrs["href"]

    def handle_endtag(self, tag):
        if tag == "a" and self.link is not None:
            self.href = None

    def handle_data(self, data):
        if data == "Скачать книгу":
            self.link = self.href

def download(url, path):
    base_url = "https://www.culture.ru"

    full_url = base_url + url
    name = url.split("/")[-1]

    print("scanning book '%s' page '%s' ..." % (name, full_url))
    res = urlopen(full_url)
    html = res.read().decode("utf-8")
    
    parser = Parser()
    parser.feed(html)

    print("downloading book '%s' from '%s' ..." % (name, parser.link))
    res = urlopen(parser.link)
    data = res.read()

    fpath = path + "/" + name
    if not fpath.endswith(".epub"):
        fpath += ".epub"
        
    print("saving book '%s' to '%s' ..." % (name, fpath))
    file = open(fpath, "wb")
    file.write(data)
    file.close()

if __name__ == "__main__":
    download("/books/188/vishnevyi-sad", ".")
