import select, socket, sys, struct, re
import proxy

KEEP_ALIVE = False

def byte2addr( b ):
	if len(b) != 6:
		raise ValueError("invalid bytes")
	host = socket.inet_ntoa(b[:4])
	port , = struct.unpack("H" , b[-2:])
	return host, port


try:
	monkey = (sys.argv[1], int(sys.argv[2]))
	key = sys.argv[3].strip()
except (IndexError, ValueError):
	print("usage: <Monkey hostname> <Monkey port> <sharing key>")
	sys.exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(bytes(key, 'utf-8'), monkey)

data, addr = sock.recvfrom(len(key) + 3)

print("connection info: ", data)
if data != b"ok" + bytes(key, 'utf-8'):
	print("invalid request")
	sys.exit(1)

sock.sendto(b'ok', monkey)
print("Waiting for other clients with sharing key " , key)
data, addr = sock.recvfrom(6)

target = byte2addr(data)

print("connection to client %s, say hello to him." % str(target))
sock.sendto(b'hello', target)
if sock.recv(6) != b'hello':
	print('Connection failed to client')
	sys.exit(1)

while True:
	rfds, _, _ = select.select([0, sock], [], [])
	if 0 in rfds:
		data = sys.stdin.readline()
		print("your message:", data)
		if not data:
			break
		sock.sendto(bytes(data, 'utf-8'), target)
	elif sock in rfds:
		data, addr = sock.recvfrom(1024)
		if re.match(b'^GETPAGE ', data):
			for line in proxy.getPage(data[8:].decode('utf-8')):
				sock.sendto(line, addr)
			print("Proxy request %s response..." % data[:8].decode('utf-8'))
			continue

		if re.match(b'^RSP', data): KEEP_ALIVE = True
		if re.match(b'^ENDRSP', data): KEEP_ALIVE = False
		if re.match(b'^(RSP|ENDREP)', data): continue
		if KEEP_ALIVE:
			print(data)
		else: 
			print(str(addr), "He/She say:\n", data.decode('utf-8'))
sock.close()

