import sys

from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView
from PyQt4.QtNetwork import QNetworkCookie

class WebView(QWebView):
	def __init__(self):
		super().__init__()
		self.load_cookies()

	def closeEvent(self, event):
		self.dump_cookies()
		super().closeEvent(event)

	def load_cookies(self, filename="cookies.bin"):
		raw = b""
		try:
			file = open(filename, "rb")
			raw = file.read()
			file.close()
		except:
			print("[warn] cannot open '%s'" % filename)
			return
		cookies = QNetworkCookie.parseCookies(raw)
		self.page().networkAccessManager().cookieJar().setAllCookies(cookies)

	def dump_cookies(self, filename="cookies.bin"):
		file = open(filename, "wb")
		cookies = self.page().networkAccessManager().cookieJar().allCookies()
		for cookie in cookies:
			file.write(cookie.toRawForm())
			file.write(b"\n")
		file.close()

def load_cookies():
	app = QApplication(sys.argv)

	browser = WebView()
	browser.load(QUrl("https://www.avito.ru"))
	browser.loadFinished.connect(lambda ok: browser.close())
	browser.show()

	app.exec_()

if __name__ == "__main__":
	app = QApplication(sys.argv)

	browser = WebView()
	browser.load(QUrl("https://www.avito.ru"))
	browser.show()

	app.exec_()
