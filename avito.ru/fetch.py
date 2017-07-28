#!/usr/bin/python3

from urllib.request import urlopen
from html.parser import HTMLParser
import xlsxwriter

site = "https://www.avito.ru"

def parse_price(pstr):
	pstr = "".join([ c for c in pstr if c in "0123456789" ])
	if len(pstr) > 0:
		pint = int(pstr)
	else:
		pint = 0
	return pint

class Parser(HTMLParser):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.level = 0
		self.stack = []
		self.entries = []

	def handle_starttag(self, tag, attrs):
		attrs = { k: v for k, v in attrs }
		if self.level > 0:
			# print(" "*self.level + "<" + tag + " " + str(attrs) + ">")
			self.level += 1
			if attrs.get("class", "") == "item-description-title-link":
				self.stack.append(("link", self.level))
				self.entries[-1]["link"] = attrs["href"]
			elif attrs.get("class", "") == "about":
				self.stack.append(("price", self.level))
		elif attrs.get("class", "") == "description item_table-description":
			# print(" "*self.level + "<" + tag + " " + str(attrs) + ">")
			self.level = 1
			self.stack.append(("desc", self.level))
			self.entries.append({})

	def handle_endtag(self, tag):
		if self.level > 0:
			if self.stack[-1][1] == self.level:
				self.stack.pop()
			self.level -= 1
			# print(" "*self.level + "</" + tag + ">")

	def handle_data(self, data):
		ldata = data.replace("\n", "").strip()
		if self.level > 0 and len(ldata) > 0:
			# print(" "*self.level + ldata)
			if self.stack[-1][0] == "link":
				self.entries[-1]["name"] = ldata
			elif self.stack[-1][0] == "price":
				self.entries[-1]["price"] = parse_price(ldata)


def search(city, query):
	mquery = query.replace(" ", "+")
	html = urlopen(site + "/" + city + "?q=" + mquery).read().decode("utf-8")

	parser = Parser()
	parser.feed(html)

	for entry in parser.entries:
		entry["query"] = query
		entry["city"] = city

	return parser.entries


exact_match = True

def filter(entry):
	qws = entry["query"].lower().split(" ")
	if exact_match:
		for qw in qws:
			if entry["name"].lower().find(qw) < 0:
				return None
	return entry


cities = [
	"novosibirsk",
	"barnaul"
]
queries = [
	"RX 480",
	"GTX 970",
]
cols = [
	"city",
	"query",
	"name",
	"link",
	"price"
]
cols_width = {
	"city": 20,
	"query": 10,
	"name": 50,
	"link": 20,
	"price": 10
}
local_cols = {
	"city":  "Город",
	"query": "Запрос",
	"name":  "Наименование",
	"link":  "Ссылка",
	"price": "Цена, руб"
}

local_cities = {
	"novosibirsk": "Новосибирск",
	"barnaul":     "Барнаул"
}

def write(ws, row, entry):
	for i, c in enumerate(cols):
		if c == "city":
			sn = entry[c]
			sn = local_cities.get(sn, sn)
			ws.write_string(row, i, sn)
		elif c == "link":
			ws.write_url(row, i, site + entry[c])
		elif c == "price":
			ws.write_number(row, i, entry[c])
		else:
			ws.write(row, i, entry[c])
				

row = 0
wb = xlsxwriter.Workbook("results.xlsx")
ws = wb.add_worksheet()
for i, c in enumerate(cols):
	ws.write_string(row, i, local_cols[c])
	if c in cols_width.keys():
		ws.set_column(i, i, cols_width[c])
row += 2

for city in cities:
	for query in queries:
		entries = sorted(search(city, query), key=lambda e: e["price"])
		for entry in entries:
			entry = filter(entry)
			if entry is None:
				continue
			#print("{")
			#for k, v in entry.items():
			#	print("\t%s: %s" % (k, v))
			#print("}")
			write(ws, row, entry)
			row += 1
		row += 1

wb.close()
