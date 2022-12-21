import socket, shutil,os, re, csv
from pathlib import Path
import logging
PORT = 9090
MAIN_DIR = Path(os.getcwd(), 'system_home')
CURR_DIR = Path(os.getcwd(), 'system_home')
user_dir =''
path = ''
login = ''
size = 0
"""
pwd - вернёт название рабочей директории
ls - вернёт список файлов в директории
ls <dirname> - вернёт список файлов в директории
mkdir <dirname>  -  создаёт директорию с указанным именем
rmdir <dirname>  -  удаляет директорию с указанным именем
rm <filename> -  удаляет файл с указанным именем
touch <filename> -  создаёт файл с указанным именем
rename <filename>  <filename2> -  переименновывает файл с указанным именем 
cat <filename>  -  вернёт содержимое файла
move <filename> <dirname> -  перемещает файл/директорию в другую директорию
"""
file_user = Path(os.getcwd(), 'file_user.csv')
def log_inf():
    logging.basicConfig(
        level=logging.DEBUG,
        format="Date: %(asctime)s | %(message)s",
        handlers=[
            logging.FileHandler("logs.log"),
            logging.StreamHandler(),
        ],
    )

def write_user(login, password):
    global file_user
    with open(file_user, "a+", newline="") as f:
        f.seek(0, 0)
        reader = csv.reader(f, delimiter=";")
        for line in reader:
            if line[0] == login:
                if line[1] == password:
                    break
                else:
                    return None
        else:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([login, password])
def write_log(msg):
    logging.info(msg)
def users(msg):
    global MAIN_DIR, CURR_DIR, user_dir, login, size
    login = msg[:msg.find("=login, ")]
    password = msg[msg.find(" "):msg.find("=password, ")].strip()
    CURR_DIR = msg[msg.find(" ", msg.find("=password, "), msg.find("=curr_dir, ")):msg.find("=curr_dir, ")].strip()
    size = msg[msg.find(" ", msg.find("=curr_dir, "), msg.find("=len, ")):msg.find("=len, ")].strip()
    msg = msg[msg.find(" ", msg.find("=len, "), msg.find("=message")):msg.find("=message")].strip()
    if login == "admin" and password == "qwerty":
        user_dir = MAIN_DIR
    else:
        user_dir = Path(MAIN_DIR, login)
        write_user(login, password)
        try:
            os.makedirs(user_dir)
        except FileExistsError:
            pass
    return user_dir, CURR_DIR, msg, login, size

def check_command(req):
    global user_dir, path
    req = users(req)
    if req:
        user_dir, CURR_DIR, msg, login, size = req
        comm, *args = msg.split()
        if CURR_DIR != login:
            t = CURR_DIR.replace("\\", "", 1)
            path = Path(user_dir, t)
        comms = {
            'ls': ls,
            'pwd': pwd,
            'mkdir': mkdir,
            'touch': touch,
            'rmdir': rmdir,
            'rename': rename,
            'rm': rm,
            'mv': move,
            'cd': cd,
            'send_from':send_from,
            'cat': cat,
            'get_to':get_to,
            'help': help
        }

        try:
            return comms[comm](*args)
        except Exception as e:
            return 'Нет такой команды'
    else:
        return 'bad password'
def check():
    global path, user_dir, CURR_DIR
    if path != "":
        if login == CURR_DIR:
            return user_dir
        elif path != user_dir:
            return path
        else:
            return user_dir
    return user_dir
def pwd():
    global user_dir, CURR_DIR, login
    root = check()
    if CURR_DIR != 'admin':
        s =''
        for i in root.parts[3:]:
            s += "\\"+i
        return s
    else:
        return str(root)
def ls(name=None):
    global user_dir
    root = check()
    if name:
        name1 = Path(root, name)
        return '; '.join(os.listdir(name1))
    return '; '.join(os.listdir(root))


def mkdir(name):
    global user_dir
    root = check()
    name = Path(root, name)
    try:
        os.mkdir(name)
        return "успешно"
    except Exception:
        return "wrong"

def rename(name1, name2):
    global user_dir
    root = check()
    name1 = Path(root, name1)
    name2 = Path(root, name2)
    try:
        os.rename(name1, name2)
        return "успешно"
    except Exception:
        return "wrong"
def cd(name):
    global user_dir, CURR_DIR, path
    root = check()
    try:
        if name == "..":
            name1 = Path(user_dir)

        else:
            name1 = Path(root, name)
        # path = Path(user_dir, name)
        os.chdir(name1)
    except:
        return CURR_DIR
    return os.getcwd()
def touch(name, text=''):
    global user_dir
    root = check()
    name = Path(root,name)
    max_size = pow(2, 20) * 10 - getting(root)
    if max_size < int(size):
        return "Нет места"
    # with open(name, 'w') as file:
    #     pass
    else:
        try:
            name.touch()
            name.write_text(text)
            return "успешно"
        except Exception:
            return "wrong touch"
def rmdir(name):
    global user_dir
    root = check()
    name = Path(root,name)
    if name.is_dir():
        shutil.rmtree(name)
        return "успешно"
    else:
        return 'Вы ввели имя не папки'
def rm(name):
    try:
        root = check()
        global user_dir
        name = Path(root,name)
        if name.is_file():
            os.remove(name)
            return "успешно"
        else:
            return 'Вы ввели имя не файла'
    except Exception:
        return "wrong rm"
def move(src, dst):
    global user_dir
    try:
        root = check()
        src = Path(root,src)
        dst = Path(root,dst)
        if src.exists():
            shutil.move(src, dst)
            return "успешно"
        else:
            return "Не существует"
    except Exception:
        return "wrong move"

def cat(name):
    try:
        global user_dir
        root = check()
        name = Path(root,name)
        if name.is_file():
            return name.read_text()
        else:
            return "Не файл"
    except Exception:
        return "wrong cat"


def help():
    return 'pwd - вернёт название рабочей директории\n' \
           'ls - вернёт список файлов в рабочей директории\n' \
           'mkdir -  создаёт директорию с указанным именем\n' \
           'rmdir -  удаляет директорию с указанным именем\n' \
           'touch -  создаёт файл с указанным именем\n' \
           'rm -  удаляет файл с указанным именем\n' \
           'move -  перемещает файл/директорию в другую директорию\n' \
           'rename -  переименновывает файл с указанным именем \n' \
           'cat -  вернёт содержимое файла\n' \
           'help - выводит справку по командам\n' \
           'exit - выход из системы'


conn =''
def getting(name):
    size = 0
    for dirpath, dirnames, file in os.walk(name):
        for f in file:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                size += os.path.getsize(fp)

    return size
def send_from(name):
    global conn, size
    root = check()
    name = Path(root, name)
    max_size = pow(2, 20) * 10 - getting(root)
    if max_size < int(size):
        return "Нет места"
    else:
        text = conn.recv(int(size)).decode()
        try:
            with open(name, 'w') as file:
                file.write(text)
            write_log("все получено")
            return f'{name}'

        except Exception:
            return 'wrong'


def get_to(name):
    global conn
    root = check()
    name = Path(root, name)
    with open(name, 'r') as file:
        text = file.read()
    conn.send(str(len(text)).encode())
    conn.send(text.encode())
    write_log("Отправлено")
    return f'{name}'

def main():
    global conn
    log_inf()
    if not MAIN_DIR.is_dir():
        mkdir(MAIN_DIR)
    os.chdir(MAIN_DIR)
    # подключаемся
    with socket.socket() as sock:
        sock.bind(('', PORT))
        sock.listen()
        print("Слушаем порт: ", PORT)
        write_log(f'Слушаем порт: {PORT}')
        while True:
            conn, addr = sock.accept()
            with conn:
                req = conn.recv(1024).decode()
                write_log("request:"+req)

                resp= check_command(req)

                write_log("response:"+str(resp))
                if resp is None:
                    resp = ''
                try:
                    conn.send(resp.encode())
                except Exception:
                    conn.send(resp)
        conn.close()


if __name__ == '__main__':
    main()