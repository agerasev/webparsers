#!/usr/bin/python3

import os
import shutil

import json
import re
from urllib.request import Request, urlopen, urlretrieve

from time import sleep
import traceback
from random import randrange


headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Accept-Language": "en-US,en;q=0.5",
	"Connection": "keep-alive",
	"Referer": "https://www.joom.com/en/",
	"Origin": "https://www.joom.com",
	"Proxy-Authorization": "".join(["0123456789abcdef"[randrange(16)] for _ in range(80)]),
}

cookies = {}

def cookies_store(d):
	s = ""
	for k, v in d.items():
		s += k + "=" + v + ";"
	return s

def cookies_load(s):
	s = re.sub("[E|e]xpires=[^;]*;", "", s)
	d = {}
	for kv in s.strip().split(","):
		(k, v) = tuple(kv.strip().split(";")[0].strip().split("="))
		d[k] = v
	return d

def request(url, data=None):
	headers["Cookie"] = cookies_store(cookies)
	if "accesstoken" in cookies.keys():
		token = cookies["accesstoken"].replace("%3D", "=")
		headers["Authorization"] = ("Bearer %s" % token)
		# print(token)
	req = Request(url, headers=headers)
	res = None
	if data is not None:
		req.add_header('Content-Type', 'application/json')
	while True:
		try:
			print("[info] send http request")
			if data is None:
				res = urlopen(req)
			else:
				res = urlopen(req, data)
			break
		except Exception as e:
			traceback.print_exc()
	cookies.update(cookies_load(res.getheader("Set-Cookie")))
	return res.read().decode("utf-8")

def loadfile(url, outfn):
	print("[info] load image")
	urlretrieve(url, outfn)

language = "en"
currency = "USD"

outdir = "output"
shutil.rmtree(outdir)

sleep(1)

os.mkdir(outdir)
dirstack = [outdir]

html = request("https://www.joom.com/en/")
cats = json.loads(re.search(r"window.__data=([^;\n]*);\n", html).group(1))

sleep(1)

def scan(idn, name, final):
	name = name.replace("/", " and ").strip(" ")
	dirstack.append(name)
	os.mkdir("/".join(dirstack))
	if final:
		out = json.loads(request(
			"https://api.joom.com/1.1/search/products?language=%s&currency=%s" % (language, currency),
			json.dumps({
				"query": "",
				"filters": [{
					"id": "categoryId",
					"value": {
						"type": "categories",
						"items": [{ "id": idn }]
					}
				}]
			}).encode("utf-8")
		))
		info = {}
		for item in out["payload"]["items"]:
			name = "%s.jpg" % item["id"]
			loadfile(item["mainImage"]["images"][-1]["url"], "%s/%s" % ("/".join(dirstack), name))
			info[item["id"]] = item
		infofile = open("/".join(dirstack) + "/info.json", "w")
		infofile.write(json.dumps(info))
		infofile.close()
	else:
		out = json.loads(request("https://api.joom.com/1.1/categories?parentId=%s&level=1&language=%s&currency=%s" % (idn, language, currency)))
		for item in out["payload"]["items"]:
			scan(item["id"], item["name"], not item["hasPublicChildren"])
	dirstack.pop()

for k, v in cats["categories"]["data"].items():
	scan(k, v["name"], False)
