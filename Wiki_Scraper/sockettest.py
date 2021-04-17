import socket
from sys import argv

s = socket.socket()
try:
    s.connect(('', int(argv[1])))
except (IndexError, ValueError):
    print("Supply the port (as an integer) to test on")
    exit(1)
s.send("https://en.wikipedia.org/wiki/System".encode())
res = ""
while 1:
    block = s.recv(1024)
    if not block:
        break
    res += block.decode()
print(res)