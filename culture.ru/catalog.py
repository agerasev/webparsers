import os 

from urllib.request import Request, urlopen
from html.parser import HTMLParser

import author


class Tag:
    def __init__(self, name, onpop=None):
        self.name = name
        self.onpop = onpop

    def pop(self):
        if self.onpop is not None:
            self.onpop()

class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack = []
        self.catalog = False
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = {k: v for k, v in attrs}
        tag = Tag(tag)

        if "id" in attrs and attrs["id"] == "catalog":
            self.catalog = True
            def onpop():
                self.catalog = False
            tag.onpop = onpop

        self.stack.append(tag)

        if "class" in attrs and "entity-card_thumbnail-link" in attrs["class"].split(" "):
            if self.catalog:
                self.links.append(attrs["href"])

    def handle_endtag(self, _tag):
        while True:
            tag = self.stack.pop()
            tag.pop()
            if tag.name == _tag:
                break

    def handle_data(self, data):
        pass

def scan():
    try:
        os.mkdir("./books")
    except FileExistsError:
        pass

    page = 0
    while True:
        page_url = "https://www.culture.ru/literature/persons?page=" + str(page + 1)
        print("scanning catalog (page %d) '%s' ..." % (page + 1, page_url))

        res = urlopen(page_url)
        html = res.read().decode("utf-8")
        
        parser = Parser()
        parser.feed(html)

        if len(parser.stack) > 0:
            raise Exception()

        if len(parser.links) > 0:
            for link in parser.links:
                author.scan(link)
        else:
            print("nothing found - scan complete")
            break

        page += 1

if __name__ == "__main__":
    scan()