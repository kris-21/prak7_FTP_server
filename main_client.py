import socket,re, os
PORT = 9090
from pathlib import Path
HOST = 'localhost'
CURR_DIR = "\\"
sock = ''
MAIN_DIR = Path(os.getcwd(), 'system_home')

def msg_user(login, password, CURR_DIR, msg, c = 0):
    return f"{login}=login, {password}=password, {CURR_DIR}=curr_dir, {c}=len, {msg}=message".encode()

def _send(login, password, CURR_DIR, req):
    global sock
    name = re.split("[ \\/]+", req)[-1]
    curr_path_file = Path(MAIN_DIR, name)
    sock.send(f'send {name}'.encode())
    with open(curr_path_file, 'r') as file:
        text = file.read()
    # sock.send(str(len(text)).encode())
    print(text.encode())
    sock.send(msg_user(login, password, CURR_DIR, text.encode(), len(text)))
    return


def _res(req):
    global sock, f1, f2, MAIN_DIR, CURR_DIR
    flag_finder = sock.recv(1024)
    name = re.split("[ \\/]+", req)[-1]
    print(name)
    length = sock.recv(1024).decode()
    text = sock.recv(len(length)).decode()
    curr_path_file = Path(MAIN_DIR, name)
    with open(curr_path_file, 'w') as file:
        file.write(text)
    return

def main():
    global sock
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    CURR_DIR = login



    print(f"Присоединились к {HOST} {PORT}")
    print('help - список команд, exit - выход')
    while True:
        req = input(CURR_DIR+'$')
        req = req.strip()
        if req == 'exit':
            break
        sock = socket.socket()
        sock.connect((HOST, PORT))
        if req.find("send_from") == 0:
            if req == "send_":
                print("Нет файла")
            else:
                _send(login, password, CURR_DIR, req)

        else:
            sock.send(msg_user(login, password, CURR_DIR, req))
            if req.find("get_to") == 0 or req == "get_to":
                _res(req)
            else:

                response = sock.recv(1024).decode()
                if req.find("cd") == 0:
                    if ".." in req:
                        CURR_DIR = login


                    else:
                        CURR_DIR = response[response.find("\\", response.find(login)):]
                else:
                    print(response)





if __name__ == '__main__':
    main()