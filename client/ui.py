import curses
import json

from select import select

class Ui:
    def __init__(self, socket, nick):
        self.prompt = "> "
        self.fmt    = "{nick} - {msg}"
        self.socket = socket
        self.nick   = nick

        stdscr = curses.initscr()
        lines, columns = stdscr.getmaxyx()

        self.winput = curses.newwin(1, columns, lines - 1, 0)
        self.wmsg = curses.newwin(lines - 1, columns, 0, 0)

        self.winput.nodelay(True)
        self.wmsg.scrollok(True)

        curses.noecho()
        curses.cbreak()

        self.winput.addstr(self.prompt)

    def __print__(self, data):
        data = json.loads(data)
        self.wmsg.addstr(self.fmt.format(**data))
        self.wmsg.addstr("\n")
        self.wmsg.refresh()

    def do_msg(self):
        while 1:
            readable, _, _ = select([self.socket], [], [], 0)
            if readable:
                data = self.socket.recv(4096)
                self.__print__(data)

    def __mkdata__(self, msg):
        data = json.dumps({"nick": self.nick, "msg": msg})
        return bytes(data, "utf-8")

    def do_input(self, inp):

        self.can_send = False
        cury, curx = self.winput.getyx()
        ch = self.winput.getch()
        if ch != curses.ERR:

            if ch == ord("\n"):
                if not inp:
                    return 1
                data = self.__mkdata__(inp)
                self.__print__(data)
                self.winput.clear()
                self.winput.addstr(self.prompt)
                self.winput.refresh()
                inp = ""
                self.can_send = True

            elif ch in [curses.KEY_BACKSPACE, ord("\b"), ord("\x7f")]:
                self.winput.delch(0, curx - 1)
                inp = inp[:-1]

            else:
                self.winput.addch(ch)
                self.winput.refresh()
                inp += chr(ch)

        return inp

    def kill(self):
        curses.endwin()
