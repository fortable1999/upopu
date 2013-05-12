#!/usr/bin/env python3.3

REMOTE_HOST = "" # change to the public remote host
REMOTE_PORT = 1414      # change to the public remote port
SHARING_KEY = "key" # choose a sharing key

from upopu import USocket
import select, sys

sock = USocket(REMOTE_HOST, REMOTE_PORT, SHARING_KEY)
sock.connect()
rl, wl, xl = select.select([sys.stdin, sock], [],[], 5)
for r in rl:
	if r is sys.stdin:
		for line in sys.stdin.readlines():
			sock.send(bytes(line, 'utf-8'))
	if r is sock:
		print(sock.recv())
		



