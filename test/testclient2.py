from upopu import USocket

sock = USocket('localhost', 51000, "testkey")
sock.connect()
print(sock.recv())
print(sock.send("Hello! from client 2"))

