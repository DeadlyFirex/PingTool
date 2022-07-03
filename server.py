import socket
from sys import argv

import threading
from random import randint
from typing import Union
from datetime import datetime

from aenum import enum


class Actions(enum):
    connect = 1
    verify = 2
    ping = 3
    fetch = 4

class Client:
    def __init__(self, name: Union[str, None], address: tuple, connection: socket.socket):
        self.name: str = name
        self.address: tuple = address,
        self.last_action: int = Actions.connect
        self.last_action_time: datetime = datetime.now()
        self.connection: socket.socket = connection


    def close_connection(self):
        if self in client_list:
            client_list.remove(self)
        self.connection.close()

    def


def log(message: str, client: Union[Client, None]):
    now = datetime.now().strftime('%H:%M:%S')
    message = message.removesuffix("\n")

    if client is None:
        print(f"[{now}] - {message}")
        return
    print(f"[{now}] ({client.address[0]}) - {message}")
    return


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

last_run = None
client_list = list()

try:
    ip_address = str(argv[1])
    port = int(argv[2])
except IndexError:
    ip_address = socket.gethostbyname(socket.gethostname())
    port = 5001


log("Booting up server", None)
server.bind((ip_address, port))
server.listen(5)


def get_all_user_names():
    result = []

    for client in client_list:
        if client.name is None:
            result.append(f"Unverified-{randint(0,999)}")
            continue
        result.append(client.name)
    return result or None


def get_user_by_name(name: str):
    for client in client_list:
        if client.name == name:
            return client
    return None


def get_user_by_address(address: str):
    for client in client_list:
        if client.address == address:
            return client
    return None


def client_thread(client: Client):
    connection = client.connection

    log("New client connected", client)
    connection.send("Connected:True\n".encode())

    while True:
        try:
            message = connection.recv(2048).decode("utf-8")

            if message:
                if client.name is None:
                    if "Name:" not in message:
                        log(f"Kicking user for bad verification: {message}", client)
                        connection.sendall("Verified:?\n".encode())
                        remove(client)
                        return
                    else:
                        client.name = message.split(":")[1].removesuffix("\n")
                        log(f"Verified user as: {client.name}", client)
                        connection.sendall(f"Verified:{client.name}\n".encode())

                elif message in ["FetchUsers:?", "FetchUsers:?\n"]:
                    result = ""
                    for i in get_all_user_names():
                        if result == "":
                            result += i
                            continue
                        result += "," + i
                    log(f"Fetched all users: {result}", client)
                    connection.sendall(f"Users:{result}\n".encode())

                elif "Ping:" in message:
                    raw_message = message.split(":")[1].removesuffix("\n")
                    target = get_user_by_name(raw_message)

                    if target is None:
                        connection.sendall("UserNotFound:?\n".encode())
                    else:
                        log(f"Sent ping to {target.name} from {client.name}", client)
                        connection.sendall(f"SentPing:{target.name}\n".encode())
                        target.connection.sendall(f"ReceivedPing:{client.name}\n".encode())

                elif "Exit:" in message:
                    connection.sendall("Bye:?\n".encode())
                    remove(client)
                    return

                else:
                    log(f"Unknown command: {message}", client)
                    connection.sendall("CommandNotFound:?\n".encode())
            else:
                log(f"Gracefully disconnecting {client.name}", client)
                remove(client)
                return
        except Exception as e:
            log(f"Force disconnecting {client.name}, due to: {e.__str__()}", client)
            remove(client)
            return


def remove(client: Client):
    if client in client_list:
        client_list.remove(client)
    client.connection.close()


while True:
    conn, addr = server.accept()

    new_user = Client(addr, None, conn)
    client_list.append(new_user)

    threading.Thread(target=client_thread, args=(new_user,)).start()

conn.close()
server.close()