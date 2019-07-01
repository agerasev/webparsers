import os
import hashlib

if __name__ == "__main__":
	books = {}

	base = "./books"

	for d in os.listdir(base):
		dp = base + "/" + d
		files = os.listdir(dp)
		if len(files) > 0: 
			for b in files:
				bp = dp + "/" + b
				if b in books:
					books[b].append(bp)
				else:
					books[b] = [bp]
		else:
			os.rmdir(dp)

	for name, files in books.items():
		if len(files) <= 1:
			continue
		hashes = []
		for fn in files:
			with open(fn, "rb") as f:
				m = hashlib.sha256()
				m.update(f.read())
				hashes.append((fn, m.digest()))
		for i, (fx, hx) in enumerate(hashes):
			for (fy, hy) in hashes[(i+1):]:
				if hx == hy:
					print("books '%s' and '%s' are the same" % (fx, fy))
