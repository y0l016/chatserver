import argparse

from socket import *

if __main__ == "__name__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar="", help="server's address")

    if args.i:
        tmp  = args.i.split(':')
        HOST = tmp[0]
        PORT = tmp[1]

    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while 1:
            message = input("Your Message: ")
            s.send(bytes(message, "utf-8"))
            print("Awaiting reply")
            reply = s.recv(1024)
            print("Received", repr(reply))
