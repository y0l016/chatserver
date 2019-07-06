from socket import *

HOST = '192.168.225.22' 

PORT = 8000
s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT)) 
s.listen(1) 
conn, addr = s.accept() 
print ('Connected by', addr) 
while True:
    data = conn.recv(1024) 
    print ("Received ", repr(data)) 
    reply = input("Reply: ")
    conn.sendall(bytes(reply, "utf-8")) 
    
conn.close()
