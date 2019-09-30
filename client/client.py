import socket

from dataclasses import dataclass

@dataclass
class User:
    nick: str
    server_addr: (str, int)
    socket: socket.socket

    def connect(self):
        self.socket.connect(self.server_addr)
        self.socket.send(bytes(self.nick, "utf-8"))

def init():
    import sys
    if len(sys.argv) == 1:
        print("server ip not provided!")
        exit(1)

    ad = sys.argv[1].split(":")
    if len(ad) == 1:
        port = 9600
    else:
        port = int(ad[1])
    saddr = (ad[0], port)
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    global USER, UI
    import os
    import ui
    nick = os.getenv("USER")
    USER = User(nick, saddr, sck)
    UI   = ui.Ui(sck, nick)

    USER.connect()

def main():
    msg_thread = threading.Thread(target=UI.do_msg)
    msg_thread.start()

    inp = ""
    while 1:
        inp = UI.do_input(inp)
        if inp == 1:
            inp = ""
            continue

        if UI.can_send:
            data = UI.__mkdata__(inp)
            if inp.startswith("/"):
                if inp[1:] in CMD:
                    data = CMD[inp[1:]](data)
            if data:
                USER.socket.send(data)

if __name__ == "__main__":
    init()
    from commands import *
    import threading
    main()
