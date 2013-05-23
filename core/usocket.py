import select, socket, sys, struct, re
from upopu.core.utils import addr2byte, byte2addr, text2seq, seq2text
from upopu.core.exceptions import *
from upopu.core.window import windowsender, windowreceiver

# CLIENT STATUS
CLIENT_UNINITIALIZED = 0
CLIENT_REQUEST_SENT = 9
CLIENT_REQUEST_ACCEPTED_BY_SERVER = 8
CLIENT_WAIT_PARING = 7
CLIENT_PAIR_OK = 6
CLIENT_SYNC = 5
CLIENT_CONNECTED = 4
CLIENT_SOCKET_CLOSED = 3
CLIENT_SYNCING = 2

class UPOPUServer(object):
	keyset = {}

	def __init__(self, port):
		self.svr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.svr_sock.bind(("", port))
	
	def serve_forever(self):
		while True:
			data, addr = self.svr_sock.recvfrom(32)
			key = data.strip()
			# print("Client connected from %s:%d, have sharing key " % addr, key)
			self.svr_sock.sendto(b"ok" + key, addr)
			data, addr = self.svr_sock.recvfrom(2)
			if data != b'ok':
				continue
			# print("request reveiced for with sharing key: ", key)
			try:
				a, b = self.keyset[key], addr
				self.svr_sock.sendto(addr2byte(a), b)
				self.svr_sock.sendto(addr2byte(b), a)
				# print("%s %s linked" %(str(a), str(b)), key)
				del self.keyset[key]
				# print("sharing key %s released" % key)
			except KeyError:
				self.keyset[key] = addr




class UPOPUSocket(object):
	# UPOPU socket object
	# wrap a udp socket, add all features

	def __init__(self, rmt_svr_host, rmt_svr_port, key):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.rmt_svr_host = rmt_svr_host
		self.rmt_svr_port = rmt_svr_port
		self.key = key
	
	def accept(self):
		print("Not implemented feature")
	
	def bind(self):
		print("Not implemented feature")
	
	def close(self):
		# send some closing message?
		self._sock.close()
	
	def connect(self):
		# as a socket
		self._sock.sendto(bytes(self.key, 'utf-8'),
				(self.rmt_svr_host, self.rmt_svr_port))
		data, addr = self._sock.recvfrom(len(self.key) + 3)

		if data != b"ok" + bytes(self.key, 'utf-8'):
			raise ServerConnectFailedException

		self._sock.sendto(b'ok', (self.rmt_svr_host, self.rmt_svr_port))
		data, addr = self._sock.recvfrom(6)
		self.target = byte2addr(data)
		self._sock.sendto(b'hello', self.target)
		if self._sock.recv(6) != b'hello':
			raise SayHelloException
		return CLIENT_CONNECTED
	
	@staticmethod
	def open(rmt_svr_host, rmt_svr_port, key, *args, **kwargs):
		# as a file
		upopusock = UPOPUSocket(rmt_svr_host, rmt_svr_port, key, *args, **kwargs)
		upopusock.connect()
		return upopusock


	# send & recv method active like a socket
	def send(self, data):
		if type(data) == str: data = bytes(data, 'utf-8')
		return windowsender(self._sock, data, target = self.target)
		# return self._sock.sendto(text, self.target)

	def recv(self):
		return windowreceiver(self._sock, self.target)
		# return self._sock.recv(size)

	# read, write, readlines, writelines methods works like a file
	def readline(self):
		data = self.recv()
		return data

	def readlines(self):
		# return bytes from socket
		self._sock.setblocking(0)
		while True:
			try:
				data = self.recv()
				yield data
			except BlockingIOError: 
				self._sock.setblocking(1)
				raise StopIteration

	def write(self, data):
		self.send(data)
		# self._sock.sendto(bytedata, self.target)

	def fileno(self):
		return self._sock.fileno()

