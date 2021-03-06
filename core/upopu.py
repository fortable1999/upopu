import select, socket, sys, struct, re
import datetime
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
	# sharing key set
	keyset = {}

	def __init__(self, port, debug = True, timeout = 120):
		self.svr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.svr_sock.bind(("", port))
		self._debug = debug
		self.timeout = timeout
	
	def serve_forever(self):
		while True:
			for key, item in self.keyset.items():
				time = item['datetime']
				if datetime.datetime.now() - time > datetime.timedelta(seconds = self.timeout):
					if self._debug: print('key %s timeout. remote from list.' % key)
					del self.keyset[key]

			data, addr = self.svr_sock.recvfrom(32)
			key = data.strip()
			if self._debug: print("Client connected from %s:%d, have sharing key " % addr, key)
			self.svr_sock.sendto(b"ok" + key, addr)
			data, addr = self.svr_sock.recvfrom(2)
			if data != b'ok':
				continue
			if self._debug: print("request reveiced for with sharing key: ", key)
			try:
				a, b = self.keyset[key]['addr'], addr
				if a == b:
					continue
				self.svr_sock.sendto(addr2byte(a), b)
				self.svr_sock.sendto(addr2byte(b), a)
				if self._debug: print("%s %s linked" %(str(a), str(b)), key)
				del self.keyset[key]
				if self._debug: print("sharing key %s released" % key)
			except KeyError:
				self.keyset[key] = {'addr': addr, 'datetime': datetime.datetime.now()}

class UPOPUSocket(object):
	# UPOPU socket object
	# wrap a udp socket, add all features

	def __init__(self, rmt_svr_host = None, rmt_svr_port = None, key = None, timeout = 30, debug = False):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.settimeout(timeout)
		self.rmt_svr_host = rmt_svr_host
		self.rmt_svr_port = rmt_svr_port
		self.key = key
		self.timeout = 30
		self._debug = debug
	
	def accept(self):
		self.connect()
		return self
	
	def alive_check(self, timeout = 10):
		return True
	
	def bind(self, remote_server):
		self.rmt_svr_host = remote_server[0]
		self.rmt_svr_port = remote_server[1]

	def set_share_key(self, key):
		self.key = key
	
	def close(self):
		# send some closing message?
		self._sock.close()
	
	def settimeout(self, timeout):
		self.timeout = timeout
		self._sock.settimeout(timeout)
	
	def connect(self):
		# as a socket
		while True:
			try:
				self._sock.sendto(bytes(self.key, 'utf-8'),
						(self.rmt_svr_host, self.rmt_svr_port))
				data, addr = self._sock.recvfrom(len(self.key) + 3)
			except socket.timeout:
				if self._debug: print("timeout. reconnecting...")
				continue
			break

		if data != b"ok" + bytes(self.key, 'utf-8'):
			raise ServerConnectFailedException

		self._sock.sendto(b'ok', (self.rmt_svr_host, self.rmt_svr_port))
		data, addr = self._sock.recvfrom(6)
		self.target = byte2addr(data)
		self._sock.sendto(b'hello', self.target)
		if self._sock.recv(6) != b'hello':
			raise SayHelloException
		return self
	
	# send & recv method active like a socket
	def send(self, data):
		if type(data) == str: data = bytes(data, 'utf-8')
		return windowsender(self._sock, data, target = self.target, debug = self._debug)

	def recv(self, length = 4096):
		# message length not implemented
		return windowreceiver(self._sock, self.target, debug = self._debug)

	def fileno(self):
		# important. for asyncore
		return self._sock.fileno()

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

	@staticmethod
	def open(rmt_svr_host, rmt_svr_port, key, *args, **kwargs):
		# as a file
		upopusock = UPOPUSocket(rmt_svr_host, rmt_svr_port, key, *args, **kwargs)
		upopusock.connect()
		return upopusock

