UPOPU is a decentralized server network.
Under development.

Usage:

server side:
  start server:
	Python3.3
	>>> from upopu.core.upopu import UPOPUServer
	>>> UPOPUServer(51234).serve_forever()

client side:
  connect to other client:

	Python3.3(from client1)
	>>> from upopu.core.upopu import UPOPUSocket
	>>> sock = UPOPUSocket("remote_host", 51234, "Hellokey")
	>>> sock.connect()

	Python3.3(from client2)
	>>> from upopu.core.upopu import UPOPUSocket
	>>> sock = UPOPUSocket("remote_host", 51234, "Hellokey")
	>>> sock.connect()

	(client 1 send message to client2)
	>>> sock.write(b'hello! I am client1')

	(client 2 get messages from client1)
	>>> for line in sock.readlines(): print(i)
	b'hello! I am client1'


