import urllib.request
import urllib

def getPage(url):
	req = urllib.request.Request(url)
	rst = urllib.request.urlopen(req)
	yield b'RSP'
	for line in rst.readlines():
		yield line
	yield b'RSPEND'
