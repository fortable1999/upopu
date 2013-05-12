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

def text2seq(text):
	if type(text) == str: text = bytes(text, 'utf-8')
	seq = {}
	seq_length = int(len(text) / 1022 + 1)
	seq[0] = seq_length
	for i in range(1, seq_length + 1):
		seq[i] = text[(i-1) *1022 : i * 1022]
	return seq

def seq2text(seq):
	text = b""
	seq_length = seq[0]
	for i in range(1, seq_length + 1):
		text += seq[i]
	return text

