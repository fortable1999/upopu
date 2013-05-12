UPOPU is a decentralized server network.
Under development.

Coder: Meng Zhao
May, 2013

Usage:

* use upopu file I/O
example. You'd like save some message to a file,
and receive these from the same file, but different machine.
Do like this:

<pre><code>    
	(from the first host)
	client1 $ echo "Hello! from client1" | dev/ufd.py

	(from the other host)
	client2 $ dev/ufd.py
	Hello! from client1
</code></pre>

* use upopu default server
upopu has a buit-in server.
It listens on port 1414, receive all connections from clients,
and paring them.

<pre><code>	   
	(to start the server)
	$ bin/upopud.py
</code></pre>

* server side:
start server:

<pre><code>
	Python3.3
	>>> from upopu.core.upopu import UPOPUServer
	>>> UPOPUServer(51234).serve_forever()
</code></pre>

* client side:
connect to other client:
<pre><code>
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
</code></pre>
