from socket import *

HOST = '' 

PORT = 8000
s = socket(AF_INET, SOCK_STREAM)s.bind((' ', 8000)) 
s.listen(1) 
conn, addr = s.accept() 
print ('Connected by', addr) 
while True:
    data = conn.recv(1024)
    print ("Received ", repr(data))
    reply = input("Reply: ")
    conn.sendall(reply) 
    
conn.close()
