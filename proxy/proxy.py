from upopu import USocket
import urllib2, select, socket

class UProxyServer(object):
	def	__init__(self, usock, port):
		self.port = port
		self._sock = usock
		self._svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._svr_sock.bind(("", self.port))
		self._svr_sock.setblocking(0)
		self._svr_sock.listen(5)
		self.rfds, self.wfds, self.xfds = [self._sock, self._svr_sock], [], []
	
	def serve_forever(self):
		while True:
			rfds, wfds, xfds = select(self.rfds, self.wfds, self.xfds)
			for rfd in rfds:
				if rfd is self._sock:
					request = rfs
				if rfd is self._svr_sock:
					pass
			for wfd in wfds:
				if wfd is self._sock:
					pass
				if wfd is self._svr_sock:
					pass

