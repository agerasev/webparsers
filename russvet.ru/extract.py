from html.parser import HTMLParser
from urllib.request import urlopen

class Parser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.level = 0
		self.stack = []

	def stack_top(self):
		if len(self.stack) > 0:
			return self.stack[-1][0]
		return None

	def stack_push(self, name):
		self.stack.append((name, self.level))

	def stack_try_pop(self):
		if len(self.stack) > 0 and self.stack[-1][1] == self.level:
			return self.stack.pop()[0]
		return None


class CategoriesParser(Parser):
	def __init__(self):
		super().__init__()
		self.entries = []

	def handle_starttag(self, tag, attrs):
		attrs = { k: v for k, v in attrs }
		self.level += 1
		if attrs.get("id", "") == "categories":
			self.stack_push("categories")
		elif self.stack_top() == "categories" and attrs.get("class", "") == "categories_items":
			self.stack_push("categories_items")
		elif self.stack_top() == "categories_items" and tag == "a":
			self.entries.append({
				"link": attrs["href"],
				"name": attrs["title"],
			})

	def handle_endtag(self, tag):
		self.stack_try_pop()
		self.level -= 1

	def handle_data(self, data):
		pass

class CountParser(Parser):
	def __init__(self):
		super().__init__()
		self.count = 1

	def handle_starttag(self, tag, attrs):
		attrs = { k: v for k, v in attrs }
		self.level += 1
		if attrs.get("class", "") == "production_pagination":
			self.stack_push("production_pagination")
		elif self.stack_top() == "production_pagination" and tag == "a":
			self.stack_push("link")

	def handle_endtag(self, tag):
		self.stack_try_pop()
		self.level -= 1

	def handle_data(self, data):
		if self.stack_top() == "link":
			try:
				n = int(data)
			except:
				pass
			else:
				if n > self.count:
					self.count = n

class ProductsParser(Parser):
	def __init__(self):
		super().__init__()
		self.entries = []

	def handle_starttag(self, tag, attrs):
		attrs = { k: v for k, v in attrs }
		self.level += 1
		if attrs.get("class", "") == "product_single_item":
			self.stack_push("product_single_item")
			self.entries.append({})

		elif self.stack_top() == "product_single_item" and attrs.get("class", "") == "brand_name hidden_child":
			self.stack_push("brand_name")
		elif self.stack_top() == "brand_name" and tag == "a":
			print("brand: " + str(attrs))
			#self.entries[-1]["brand"] = attrs["title"]

		elif self.stack_top() == "product_single_item" and attrs.get("class", "") == "product_item_visible":
			self.stack_push("product_item_visible")
		elif self.stack_top() == "product_item_visible" and tag == "a":
			print("item: " + str(attrs))
			#self.entries[-1]["link"] = attrs["href"]
			#self.entries[-1]["name"] = attrs["title"]

		elif self.stack_top() == "product_single_item" and attrs.get("class", "") == "product_item_visible":
			self.stack_push("product_item_visible")
		elif self.stack_top() == "product_item_visible" and tag == "ins":
			self.stack_push("price")


	def handle_endtag(self, tag):
		self.stack_try_pop()
		self.level -= 1

	def handle_data(self, data):
		if self.stack_top() == "price":
			print("price: " + data)
			self.entries[-1]["price"] = data


data = urlopen("http://russvet.ru/products/").read().decode("utf-8")
parser = CategoriesParser()
parser.feed(data)
categories = parser.entries

# for cat in categories:
cat = categories[2]
data = urlopen("http://russvet.ru" + cat["link"]).read().decode("utf-8")
parser = CountParser()
parser.feed(data)
count = parser.count
print(cat["name"], count)

products = []
parser = ProductsParser()
parser.feed(data)
products.extend(parser.entries)
print("page %d" % 1)
print(parser.entries)
for i in range(2, count + 1):
	data = urlopen("http://russvet.ru" + cat["link"] + "?PAGEN_1=" + str(i)).read().decode("utf-8")
	parser.entries.clear()
	parser.feed(data)
	products.extend(parser.entries)
	print("page %d" % i)
	print(parser.entries)
