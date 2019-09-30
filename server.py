import json
import os
import socket

from select import select

SERV_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
NICKS       = {}
SOCKETS     = []
BANNED      = []
OP          = []

def send_only(data, send_to):
    try:
        send_to.send(data)
    except:
        data_dict = json.loads(data)
        del NICKS[data_dict.get("nick")]
        SOCKETS.remove(sck)

def send_all(data, sent_from):
    pass_scks = [SERV_SOCKET, sent_from]
    for sck in SOCKETS:
        if sck not in pass_scks:
            print(f"sending to {sck}")
            send_only(data, sck)

def gen_msg(msg):
    msg = { "nick": "server", "msg": msg }
    return bytes(json.dumps(msg), "utf-8")

def handle_cmd(sck, data):

    cmd = data.get("msg")[1:]
    addr = sck.getpeername()
    nick = data.get("nick")

    if cmd.startswith("ban"):
        if addr not in OP:
            msg = gen_msg("you dont have permission to use this command")
            ok  = send_only(msg, sck)
            return False
        return ban(cmd.split()[1:])

    elif cmd.startswith("disconnect"):
        SOCKETS.remove(addr)
        del NICKS[nick]
        return gen_msg(f"{nick} disconnected")

    elif cmd.startswith("nick"):
        new_nick = cmd.split()[1:]
        del NICKS[nick]
        NICKS[new_nick] = addr
        return gen_msg(f"{nick} is now {new_nick}")
    else:
        return data

def ban(clients):
    msg = "banned "
    nc = len(clients) - 1

    for n, i in enumerate(clients):
        addr = NICKS.get(i)

        if addr in BANNED:
            continue

        BANNED.append(addr)
        SOCKETS.remove(addr)
        del NICKS[i]

        msg += i
        if n != nc:
            msg += " "

    return gen_msg(msg)

def list_users(send_to):
    msg = "active users\n"
    nc  = len(NICKS) - 1
    for n, i in NICKS:
        msg += i
        if n != nc:
            msg += " "
    send_only(gen_msg(msg), send_to)

def init():
    host = socket.gethostbyname(socket.gethostname())
    saddr = (host, 9600)
    SERV_SOCKET.bind(saddr)
    SERV_SOCKET.listen()
    SOCKETS.append(SERV_SOCKET)
    NICKS["server"] = saddr

    def read_file(path):
        res = []
        if os.path.isfile(path):
            with open(path) as f:
                for i in f.read().split("\n"):
                    a, p = i.split()
                    p = int(p)
                    res.append((a, p))
        return res

    OP     = read_file("op")
    BANNED = read_file("banned")

def on_kill():
    SERV_SOCKET.close()
    def write_file(path, lst):
        with open(path, 'w') as f:
            for i in lst:
                f.write(f"{i[0]} {i[1]}\n")
    write_file("op", OP)
    write_file("banned", BANNED)

def main():
    readable, _, _ = select(SOCKETS, [], [], 0)
    for sck in readable:

        if sck == SERV_SOCKET:
            sockfd, addr = SERV_SOCKET.accept()

            if addr in BANNED:
                send_only(gen_msg("you are banned"), sockfd)

            else:
                nick = sockfd.recv(4096)
                send_all(gen_msg(f"{nick.decode()} connected"),
                         SERV_SOCKET)
                SOCKETS.append(sockfd)
                NICKS[nick] = addr

        else:
            try:
                data = sck.recv(4096)

                data_dict = json.loads(data)
                if data_dict.get("msg").startswith("/"):
                    data = handle_cmd(sck, data_dict)

                    if not data:
                        continue
                send_all(data, sck)

               except ConnectionResetError:
                   addr = sck.getpeername()
                   nick = ""
                   for k, v in NICKS.items():
                       if v == addr:
                           nick = k
                   if nick:
                       send_all(gen_msg(f"{nick.decode()} disconnected"),
                                SERV_SOCKET)
                       del NICKS[nick]
                   SOCKETS.remove(sck)

if __name__ == "__main__":
    init()
    while 1:
        try:
            main()
        except KeyboardInterrupt:
            break
    on_kill()
