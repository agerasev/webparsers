#!/usr/bin/python3

import json
from urllib.request import Request, urlopen
import openpyxl
import xlsxwriter


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"}

ifn = "in.xlsx"
iwb = openpyxl.load_workbook(ifn)
iws = iwb[iwb.get_sheet_names()[0]]

words = []

k = 0
while True:
	word = iws.cell(row=(1 + k), column=1).value
	if word is None:
		break;
	word = str(word).strip()
	words.append(word)
	k += 1

synonyms = []
encoding = "utf-8"
for word in words:
	print("get '%s'" % word)
	req = Request(
		"http://synonymonline.ru/assets/json/synonyms.json",
		data=("word=%s" % word).encode(encoding),
		headers=headers
	)
	res = urlopen(req).read().decode(encoding)
	synonyms.append(json.loads(res))

ofn = "out.xlsx"
owb = xlsxwriter.Workbook(ofn)
ows = owb.add_worksheet()
for i, res in enumerate(synonyms):
	ows.write(i, 0, res["word"])
	ows.write(i, 1, res["word_baseform"])
	ows.write(i, 2, ", ".join(res["synonyms"]))
owb.close()
