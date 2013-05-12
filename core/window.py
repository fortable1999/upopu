import socket, select, struct, hashlib
from upopu.core.exceptions import *
def windowsender(sock, data, target = None, timeout = 5, windows_size = 8, pkg_size = 1024):
	# pkg[0]: "0<seq length>"
	# pkg[i]: "<i><data>"
	# 1. CLIENT A "0SD<SEQ_LENGTH>" -> CLIENT B
	# 2. CLIANT A <- "0OK<SEQ_LENGTH>" CLIENT B
	# 1. CLIENT A "1<DATA>" -> CLIENT B
	# 2. CLIANT A <- "1OK" CLIENT B
	data_seq = {} # save data seq
	if type(data) == str:
		data = bytes(data, 'utf-8')
	data = data + bytes(hashlib.md5(data).hexdigest(), 'utf-8')
	seq_length = int(len(data) / (pkg_size - 2) + 1)
	data_seq_status = { i : "NOTSEND" for i in range(seq_length + 1)}
	data_seq[0] =struct.pack("H", 0) + b"SD" + struct.pack("H", seq_length)
	for i in range(1, seq_length + 1):
		data_seq[i] = struct.pack("H", i) + data[(i-1) * (pkg_size - 2): i * (pkg_size - 2)]
	
	sock.settimeout(timeout)
	sock.sendto(data_seq[0], target)
	while True:
		try:
			pkg, addr = sock.recvfrom(pkg_size)
		except socket.timeout:
			sock.sendto(data_seq[0], target)
			continue
		if addr[1] != target[1]: 
			continue
		if pkg != struct.pack("H", 0) + b"OK" + struct.pack("H", seq_length):
			sock.sendto(data_seq[0], target)
			continue
		data_seq_status[0] = "SENDOK"
		break

	window_index = range(1, min(windows_size + 1, seq_length + 1))

	readable, writable, exceptional = [], [sock], []
	sock.setblocking(0)
	while True:
		rl, wl, _ = select.select(readable, writable, exceptional, timeout)
		if not wl and not rl:
			# timeout
			writable = [sock]
		if wl:
			if len(window_index) == 0:
				sock.setblocking(1)
				return seq_length
			writer = wl[0]
			for idx in window_index:
				if data_seq_status[idx] != "SENDOK":
					writer.sendto(data_seq[idx], target)
					data_seq_status[idx] = "SEND"
			readable = [sock]
			if all(map(lambda i:data_seq_status[i] == "SENDOK", window_index)):
				writable = []

		if rl:
			reader = rl[0]
			pkg, addr = reader.recvfrom(pkg_size)
			pkg_idx, = struct.unpack("H", pkg[:2])
			pkg_data = pkg[2:]
			if pkg_idx in window_index:
				data_seq_status[pkg_idx] = "SENDOK"
				if pkg_idx == min(window_index):
					window_index = range(min(window_index[0] + 1, seq_length + 1), min(window_index[-1] + 2,seq_length + 1))
					if len(window_index) == 1:
						sock.setblocking(1)
						return seq_length
					writable = [sock]

def windowreceiver(sock, target = None, pkg_size = 1024):
	data_seq = {}
	while True:
		pkg, addr = sock.recvfrom(pkg_size)
		if not target:
			target = addr
		if not target and target != addr:
			continue
		pkg_idx, = struct.unpack("H", pkg[:2])
		seq_length, = struct.unpack("H", pkg[-2:])
		if pkg_idx == 0:
			data_seq[0] = seq_length
			msg = struct.pack("H", pkg_idx) + b'OK' + struct.pack("H", seq_length)
			sock.sendto(msg, target)
			break
	while True:
		pkg, addr = sock.recvfrom(pkg_size)
		pkg_idx, = struct.unpack("H", pkg[:2])
		pkg_data = pkg[2:]
		if pkg_idx in range(1, seq_length + 1):
			data_seq[pkg_idx] = pkg_data
			response_msg = struct.pack("H", pkg_idx) + b'OK'
			sock.sendto(response_msg, target)
		if len(data_seq) == data_seq[0] + 1:
			break
	return handle_data_seq(data_seq)

def handle_data_seq(data_seq):
	seq_length = data_seq[0]
	data = b""
	for i in range(1, seq_length + 1):
		data += data_seq[i]
	
	checksum = data[-32:]
	data = data[:-32]
	if checksum != bytes(hashlib.md5(data).hexdigest(), 'utf-8'):
		raise DataChecksumException
	return data

