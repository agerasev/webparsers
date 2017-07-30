from html.parser import HTMLParser

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
			elif attrs.get("class", "") == "date c-2":
				self.stack.append(("date", self.level))
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
				self.entries[-1]["price"] = self.parse_price(ldata)
			elif self.stack[-1][0] == "date":
				self.entries[-1]["date"] = ldata

	def parse_price(self, pstr):
		pstr = "".join([ c for c in pstr if c in "0123456789" ])
		if len(pstr) > 0:
			pint = int(pstr)
		else:
			pint = 0
		return pint
