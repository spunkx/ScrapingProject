import socket
import signal

#send and recieve data
#sockets expect information as bytes
#it is import to ensure these are "null" terminated in c
#python usage is likely different... but still worry about it
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 1337
s.connect(('127.0.0.1', port))
print(s.recv(1024).decode())
query = input(s.recv(1024).decode())
s.send(query.encode())
imgNumb = input(s.recv(1024).decode())
s.send(imgNumb.encode())
s.close()