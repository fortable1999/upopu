#UPOPU
UPOPU is a decentralized server network.
Under development.

Usage:
##Use as a file for I/O:

example, pip a string from client1 use the file interface,
and get the output from the client2:

	client1 $ echo 'Hello from client1' | dev/ufd.py

	client2 $ dev/ufd.py
	Hello from client1

##Use the default 
	default server will work on 1414 port on this machine,
	it will receiving all income connections and get a pair for their key.
	
	$ bin/upopud.py
	(Press ctrl-c to terminate the server)

##Programming usage

###server side:
  start server:

	Python3.3
	>>> from upopu import UServer
	>>> UServer(1414).serve_forever()

###client side:
  connect to other client:

	Python3.3(from client1)
	>>> from upopu import USocket
	>>> sock = USocket("remote_host", 1414, "Hellokey")
	>>> sock.connect()

	Python3.3(from client2)
	>>> from upopu import USocket
	>>> sock = USocket("remote_host", 1414, "Hellokey")
	>>> sock.connect()

	(client 1 send message to client2)
	>>> sock.write(b'hello! I am client1')

	(client 2 get messages from client1)
	>>> for line in sock.readlines(): print(i)
	b'hello! I am client1'

