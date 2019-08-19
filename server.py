import socket

from select import select

HOST        = ""
PORT        = 9000
SERV_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_LIST = []

def init():
    SERV_SOCKET.bind((HOST, PORT))
    SERV_SOCKET.listen()
    SOCKET_LIST.append(SERV_SOCKET)

def main():
    readable, _, _ = select(SOCKET_LIST, [], [], 0)

    for sck in readable:
        if sck == SERV_SOCKET:
            # a new client has connected
            # sockfd - socket object representing client
            sockfd, _ = SERV_SOCKET.accept()
            SOCKET_LIST.append(sockfd)
        else:
            # data is sent from the client
            try:
                data = sck.recv()
                if data:
                    # send data to all clients
                    send(data, sck)
                else:
                    # client disconnected
                    if sck in SOCKET_LIST: SOCKET_LIST.remove(sck)
                    # TODO: send some other data
            except:
                pass

def send(data, sent_from):
    pass_scks = [SERV_SOCKET, sent_from]
    for sck in SOCKET_LIST:
        if sck not in pass_scks:
            try:
                sck.send(data)
            except:
                # broken client. prolly disconnected
                sck.close()
                SOCKET_LIST.remove(sck)

if __name__ == "__main__":
    init()
    while 1:
        main()
    SERV_SOCKET.close()
