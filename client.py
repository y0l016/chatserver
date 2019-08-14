from socket import *

HOST = '157.51.128.179:60364'
PORT = 8000
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, 8000)) 
while True:
    message = input("Your Message: ")
    s.send(bytes(message,"utf-8"))
    print ("Awaiting reply")
    reply = s.recv(1024) 
    print ("Received ", repr(reply))

s.close()
