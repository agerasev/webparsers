#!/usr/bin/python3

import json
import re
from urllib.request import Request, urlopen
import xlsxwriter

from htmlparser import Parser

cookies = {}

def generate_cookies(filename="cookies.bin"):
	req = Request(
		"https://www.avito.ru/",
		headers={
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Connection": "keep-alive",
		}
	)
	res = urlopen(req)
	print(str(res.getcode()) + " - cookies")
	raw_cookies = res.getheader("Set-Cookie")
	print(raw_cookies)
	file = open(filename, "w")
	file.write(raw_cookies)
	file.close()

def load_cookies(filename="cookies.bin"):
	file = open(filename, "r")
	s = file.read()
	cookies.clear()
	s = re.sub("expires=[^;]*;", "", s)
	for kv in s.strip().split(","):
		(k, v) = tuple(kv.strip().split(";")[0].strip().split("="))
		cookies[k] = v
	file.close()

try:
	load_cookies()
except:
	print("error loading cookies file, generating new one ...")
	generate_cookies()
	load_cookies()
print(cookies)

def search(city, query):
	mquery = query.replace(" ", "+")
	req = Request(
		"https://www.avito.ru/" + city + "?q=" + mquery,
		headers={
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Connection": "keep-alive",
			"Cookie": ";".join(["%s=%s" % (k,v) for k,v in cookies.items()]),
		}
	)
	res = urlopen(req)
	print(str(res.getcode()) + " - %s, %s" % (city, query))
	html = res.read().decode("utf-8")

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

qfile = open("queries.json", "r", encoding="utf-8")
qdata = json.loads(qfile.read())
qfile.close()
print(qdata)

cities = [ c[0] for c in qdata["cities"] ]
cities_names = { c[0]: c[1] for c in qdata["cities"] }

queries = qdata["queries"]
cols = [
	"city",
	"query",
	"name",
	"link",
	"date",
	"price",
]
cols_width = {
	"city": 20,
	"query": 10,
	"name": 50,
	"link": 20,
	"price": 10,
	"date": 20
}
cols_names = {
	"city":  "Город",
	"query": "Запрос",
	"name":  "Наименование",
	"link":  "Ссылка",
	"price": "Цена, руб",
	"date": "Дата"
}

def write(ws, row, entry):
	for i, c in enumerate(cols):
		if c == "city":
			sn = entry[c]
			sn = cities_names.get(sn, sn)
			ws.write_string(row, i, sn)
		elif c == "link":
			ws.write_url(row, i, "https://www.avito.ru" + entry[c])
		elif c == "price":
			ws.write_number(row, i, entry[c])
		else:
			ws.write(row, i, entry[c])
				

row = 0
wb = xlsxwriter.Workbook("results.xlsx")
ws = wb.add_worksheet()
for i, c in enumerate(cols):
	ws.write_string(row, i, cols_names[c])
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

try:
	wb.close()
except:
	print("Cannot save the workbook, maybe it's opened by you? Please, close all programs that use it, and restart parser")
