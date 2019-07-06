from socket import *

HOST = 'localhost'
PORT = 8000
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT)) # client-side, connects to a host
while True:
    message = input("Your Message: ")
    s.send(bytes(message, "utf-8"))
    print ("Awaiting reply")
    reply = s.recv(1024) # 1024 is max data that can be received
    print ("Received ", repr(reply))

s.close()
