from socket import *

HOST = ''
PORT = 8000
s = socket(AF_INET, SOCK_STREAM)
s.connect((' ', 8000)) 
while True:
    message = input("Your Message: ")
    s.send(message)
    print ("Awaiting reply")
    reply = s.recv(1024) 
    print ("Received ", repr(reply))

s.close()
