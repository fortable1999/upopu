from upopu import USocket

sock = USocket('upopu-root.org', 1414, "testkey", debug = True)
sock.connect()
fp = open('testpng2.png', 'wb')
data = sock.recv()
print('data recved')
fp.write(data)
print(sock.send("Hello! from client 2"))

