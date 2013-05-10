import socket, struct

def byte2addr( b ):
	if len(b) != 6:
		raise ValueError("invalid bytes")
	host = socket.inet_ntoa(b[:4])
	port , = struct.unpack("H" , b[-2:])
	return host, port

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
