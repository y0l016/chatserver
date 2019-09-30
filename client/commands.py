import json

def change_nick(data):
    data_dict = json.loads(data)
    USER.nick = data_dict.get("nick")
    UI.nick   = USER.nick
    return data

def disconnect(data):
    USER.socket.send(data)
    USER.socket.close()
    UI.kill()
    return False

def connect(data):
    dat = json.dumps({"nick": "client", "msg": "connected!"})
    data_dict = json.loads(data)
    addr = data_dict.get("msg").split()[1]
    addr = addr.split(":")
    if len(addr) == 1:
        port = 9600
    else:
        port = addr[1]
    USER.serv_addr = (addr[0], port)
    UI.__print__(dat)
    return False

def prompt(data):
    msg = json.loads(data).get("msg")
    new_prompt = msg[len("/prompt "):]
    UI.prompt = new_prompt
    return False

def fmt(data):
    msg = json.loads(data).get("msg")
    new_fmt = msg[len("/fmt "):]
    UI.fmt = new_fmt
    return False

def ping(data):
    dat = json.dumps({"nick": "client", "msg": "pong!"})
    UI.__print__(data)
    return False

def switch_case(data):
    data = json.loads(data)
    msg = data.get("msg")[len("/switch-case "):]
    return UI.__mkdata__(msg.swapcase())

CMD = { "nick": change_nick,      "ping": ping,
        "disconnect": disconnect, "switch-case": switch_case,
        "connect": connect, "fmt": fmt, "prompt": prompt}
