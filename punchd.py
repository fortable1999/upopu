import socket, struct, sys

def addr2byte(addr):
	host, port = addr
	try: 
		host = socket.gethostbyname(host)
	except (socket.gaierror, socket.error):
		raise ValueError('invalid host')
	try:
		port = int(port)
	except ValueError:
		raise ValueError('invalid port')
	b = socket.inet_aton(host)
	b += struct.pack("H", port)
	return b

port = 51515
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", port))
print("listening on port %d" % port)

keyset = {}
while True:
	data, addr = sock.recvfrom(32)
	key = data.strip()
	print("Client connected from %s:%d, have sharing key " % addr, key)
	sock.sendto(b"ok" + key, addr)
	data, addr = sock.recvfrom(2)
	if data != b'ok':
		continue

	print("request reveiced for with sharing key: ", key)

	try:
		a, b = keyset[key], addr
		sock.sendto(addr2byte(a), b)
		sock.sendto(addr2byte(b), a)
		print("%s %s linked" %(str(a), str(b)), key)
		del keyset[key]
		print("sharing key %s released" % key)
	except KeyError:
		keyset[key] = addr

