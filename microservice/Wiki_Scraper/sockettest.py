import socket
from sys import argv

s = socket.socket()
try:
    s.connect(('', int(argv[1])))
except (IndexError, ValueError):
    print("Supply the port (as an integer) to test on")
    exit(1)


s.send("https://en.wikipedia.org/wiki/System".encode())  # .encode takes the URL string and turns it into a bytes object
res = ""
while 1:
    block = s.recv(1024)  # recieve in blocks of 1024 bytes
    if not block:  # if the connection is closed
        break
    res += block.decode()  # append the string representation of current block
print(res)
