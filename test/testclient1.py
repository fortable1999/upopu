from upopu import USocket

sock = USocket('upopu-root.org', 1414, "testkey", debug = True)
sock.connect()
fp = open('testpng.png', 'rb')
data = fp.read()
print(sock.send(data))
print(sock.recv())

