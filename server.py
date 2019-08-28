import socket

from select import select

HOST        = ""
PORT        = 9000
SERV_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_LIST = {}
BAN_LIST    = {}
OP_LIST     = []

# utils

def send_all(data, sent_from):
    """
    send data to everyone except sent_from.
    """
    pass_scks = [SERV_SOCKET, sent_from]
    for sck in SOCKET_LIST.values():
        if sck not in pass_scks:
            try:
                sck.send(data)
            except:
                # broken client. prolly disconnected
                addr, _ = sck.getpeername()
                sck.close()
                SOCKET_LIST.remove(addr)

def send_only(data, send_to):
    """
    send data only to send_to socket
    returns True if succeded
    """
    try:
        send_to.send(data)
    except:
        return False

def gen_msg(msg):
    """
    generate message that will be sent by the server
    """
    return { "nick": "server", "msg": msg }

# cmds
def ban(clients):
    """
    ban clients
    returns a message from the server saying the clients are banned
    """
    msg = ""
    nc = len(clients) - 1
    for n, i in enumerate(clients):
        addr, _ = i.getpeername()
        if addr in BAN_LIST:
            continue
        BAN_LIST[addr] = i
        SOCKET_LIST.pop(addr)
        msg += f"server: banned {addr}"
        if n != nc:
            msg += "\n"
    return gen_msg(msg)

def handle_cmd(sock, data):
    """
    parse the command and handle the command.
    arguments:
    sock - sender's socket
    data - sender's msg data
    """
    cmd = data.get("msg")[1:]
    addr, _ = sock.getpeername()
    if cmd.startswith("ban"):
        if addr not in OP_LIST:
            msg = gen_msg("you dont have permission to use this command")
            ok = send_only(msg, sock)
            if not ok:
                sock.close()
                SOCKET_LIST.remove(addr)
                return gen_msg(f"{addr} disconnected")
            else:
                return False
        return ban(cmd.split()[1:])
    elif cmd.startswith("disconnect"):
        SOCKET_LIST.pop(addr)
        # TODO: should we make the nick server?
        # actually should we even send this message to people?
        return gen_msg(f"{addr} disconnected")
    elif cmd.startswith("list"):
        # send the user list to sender socket
        clients = ""
        ns = len(SOCKET_LIST)
        for n, i in SOCKET_LIST:
            clients += i
            if n != ns:
                clients += "\n"
        send_only(gen_msg(clients), sock)
        return False

def init():
    SERV_SOCKET.bind((HOST, PORT))
    SERV_SOCKET.listen()
    SOCKET_LIST[HOST] = SERV_SOCKET

def main():
    readable, _, _ = select(SOCKET_LIST.values(), [], [], 0)

    for sck in readable:
        if sck == SERV_SOCKET:
            # a new client has connected
            # sockfd - socket object representing client
            # addr - address of the client (would be ip in our case)
            sockfd, addr = SERV_SOCKET.accept()
            SOCKET_LIST[addr] = sockfd
        else:
            # data is sent from the client
            try:
                data = sck.recv()
                if data:
                    if data.get("msg").startswith('/'):
                        data = handle_cmd(sck, data)
                        # client did an oopsie or don't bother to send anything
                        if not data:
                            continue
                    # send data to all clients
                    send_all(data, sck)
                else:
                    # client disconnected
                    addr, _ = sck.getpeername()
                    if addr in SOCKET_LIST:
                        SOCKET_LIST.remove(addr)
                    # TODO: send some other data
            except:
                pass

if __name__ == "__main__":
    init()
    while 1:
        main()
    SERV_SOCKET.close()
