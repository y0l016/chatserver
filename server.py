import json
import socket

from select import select

HOST        = "localhost"
PORT        = 9001
SERV_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_LIST = {}
BAN_LIST    = []
OP_LIST     = []

# utils

def send_all(data, sent_from):
    """
    send data to everyone except sent_from.
    """
    pass_scks = [SERV_SOCKET, sent_from]
    for sck in [i[-1] for i in SOCKET_LIST.values()]:
        if sck not in pass_scks:
            try:
                sck.send(data)
            except:
                # broken client. prolly disconnected
                addr, _ = sck.getpeername()
                sck.close()
                SOCKET_LIST.pop(addr)

def send_only(data, send_to):
    """
    send data only to send_to socket
    returns True if succeded
    """
    try:
        send_to.send(data)
    except: pass # TODO: handle this properly

def gen_msg(msg):
    """
    generate message that will be sent by the server
    """
    msg = { "nick": "server", "msg": msg }
    return bytes(json.dumps(msg), "utf-8")

# cmds

def ban(clients):
    """
    ban clients
    returns a message from the server saying the clients are banned
    """
    msg = "banned"
    nc = len(clients) - 1
    for n, i in enumerate(clients):
        addr, _ = i.getpeername()
        nick = SOCKET_LIST.get(addr)[0]
        if addr in BAN_LIST:
            continue
        BAN_LIST.append(addr)
        SOCKET_LIST.pop(addr)
        msg += nick
        if n != nc:
            msg += " "
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
    nick = SOCKET_LIST.get(addr)[0]
    if cmd.startswith("ban"):
        if addr not in OP_LIST:
            msg = gen_msg("you dont have permission to use this command")
            ok = send_only(msg, sock)
            if not ok:
                sock.close()
                SOCKET_LIST.remove(addr)
                return gen_msg(f"{nick} disconnected")
            else:
                return False
        return ban(cmd.split()[1:])
    elif cmd.startswith("disconnect"):
        SOCKET_LIST.pop(addr)
        return gen_msg(f"{nick} disconnected")
    elif cmd.startswith("list"):
        # send the user list to sender socket
        clients = ""
        ns = len(SOCKET_LIST)
        for n, i in SOCKET_LIST:
            clients += i[0]
            if n != ns:
                clients += "\n"
        send_only(gen_msg(clients), sock)
        return False
    elif cmd.startswith("nick"):
        new_nick = cmd.split()[1:]
        for i in SOCKET_LIST:
            if i == addr:
                SOCKET_LIST[addr] = (new_nick, sock)
                break
        return gen_msg(f"{nick} is now {new_nick}")
    else:
        return data

def init():
    SERV_SOCKET.bind((HOST, PORT))
    SERV_SOCKET.listen()
    SOCKET_LIST[HOST] = ("server", SERV_SOCKET)
    # dont think theres any cleaner way to do this :/
    try:
        with open("op") as f:
            # using this instead of readlines because readlines have \n
            # at the end of each line which we DO NOT want
            OP_LIST = f.read().split("\n")
    except: pass
    try:
        with open("ban") as f:
            # the same applies here too
            BAN_LIST = f.read().split("\n")
    except: pass

def main():
    readable, _, _ = select([i[-1] for i in SOCKET_LIST.values()], [], [], 0)

    for sck in readable:
        if sck == SERV_SOCKET:
            # a new client has connected
            # sockfd - socket object representing client
            # addr - address of the client (would be ip in our case)
            sockfd, addr = SERV_SOCKET.accept()
            # on connect, we expect the client to send its nickname
            nick = sockfd.recv(4096)
            SOCKET_LIST[addr] = (nick, sockfd)
        else:
            # data is sent from the client
            try:
                data = sck.recv(4096)
                if not data:
                    # client disconnected
                    addr, _ = sck.getpeername()
                    nick = SOCKET_LIST.get(addr)[0]
                    if addr in SOCKET_LIST:
                        SOCKET_LIST.pop(addr)
                    send_all(gen_msg(f"{nick} disconnected"), SERV_SOCKET)
                try:
                    data = json.loads(data)
                except:
                    # client sent the nickname
                    continue
                if data.get("msg").startswith('/'):
                    data = handle_cmd(sck, data)
                    # client did an oopsie or don't bother to send anything
                    if not data:
                        continue
                data = json.dumps(data)
                # send data to all clients
                send_all(data, sck)
            except:
                pass

def on_kill():
    SERV_SOCKET.close()
    with open("op") as f:
        f.writelines(OP_LIST)
    with open("ban") as f:
        f.writelines(BAN_LIST)

if __name__ == "__main__":
    init()
    while 1:
        try:
            main()
        except KeyboardInterrupt:
            on_kill()
            exit(0)
    on_kill()
