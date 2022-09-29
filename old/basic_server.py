import logging
import socket
import threading

from datetime import datetime
from sys import argv
from typing import Union


def PerformLogging(logger: Union[logging.Logger, None], level: int, message: Union[str, None]):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            if logger is None:
                server_logger.log(level, message or "no message")
            f(*args, **kwargs)

        return wrapped_f

    return wrap


class Client:
    def __init__(self, name: Union[str, None], address: tuple, connection: socket.socket):
        self.name: Union[str, None] = name
        self.address: tuple = address,
        self.connection: socket.socket = connection
        self.logger: Union[logging.Logger, None] = None
        self.thread: Union[threading.Thread, None] = None

    @PerformLogging(None, logging.DEBUG, "Sending message")
    def send(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    @PerformLogging(None, logging.DEBUG, "Sending message, then disconnecting")
    def send_then_disconnect(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.close_connection()

    @PerformLogging(None, logging.DEBUG, "Sending message, then disconnecting")
    def verify(self, name: str):
        if name.__len__() > 25:
            self.send_then_disconnect("Error:?")
        self.name = name.split(":")[1].removesuffix("\n")
        self.logger = logging.getLogger(f"Clients.{self.name}")

    def close_connection(self, reason: Union[str, None] = None):
        if self.logger is None:
            clients_logger.info(f"Manually disconnecting {self.address[0]} for: {reason or 'no reason specified'}")
        self.logger.warning(f"Manually disconnecting {self.name} for: {reason or 'no reason specified'}")
        if self in client_list:
            client_list.remove(self)
        self.connection.close()

    def register_thread(self, thread_address: threading.Thread):
        self.thread = thread_address


class Utilities:
    @staticmethod
    def get_all_user_names():
        result = list()

        for client in client_list:
            if client.name is None:
                continue
            result.append(client.name)
        return result or None

    @staticmethod
    def get_all_user_names_raw():
        result = str()

        for client in client_list:
            if client.name is None:
                continue
            if result == str():
                result.__add__(client.name)
            else:
                result.__add__(f",{client.name}")
        return result or None

    @staticmethod
    def get_user_by_name(name: str):
        for client in client_list:
            if client.name == name:
                return client
        return None

    @staticmethod
    def get_user_by_address(address: str):
        for client in client_list:
            if client.address == address:
                return client
        return None

    @staticmethod
    def handle_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[1].removesuffix("\n")

    @staticmethod
    def strip_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[0].removesuffix("\n")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_logger = logging.getLogger("Server")
clients_logger = logging.getLogger("Clients")
logging.basicConfig(format=f"[%(levelname)s] [{datetime.now().strftime('%H:%M:%S')}] [%(name)s] - %(message)s",
                    level=logging.DEBUG)
client_list = list()

try:
    ip_address = str(argv[1])
    port = int(argv[2])
except IndexError:
    ip_address = socket.gethostbyname(socket.gethostname())
    port = 5001

server_logger.log(logging.CRITICAL, f"Booting up server on {ip_address}:{port}")
server.bind((ip_address, port))
server.listen(5)


def client_thread(client: Client):
    connection = client.connection

    client.send("Connected:?")

    while True:
        try:
            message = connection.recv(2048).decode("utf-8") \
                .removeprefix("\n") \
                .removesuffix("\n")

            if message:
                if client.name is None:
                    if "Name:" not in message:
                        client.logger.error(f"Kicking user for bad verification")
                        client.send_then_disconnect("Error:?")
                        return
                    client.name = Utilities.handle_argument(message)
                    client.logger = logging.getLogger(f"Clients.{client.name}")
                    client.logger.info(f"Verified user as: {client.name}")
                    client.send(f"Verified:{client.name}")

                match Utilities.strip_argument(message):
                    case "Ping":
                        username = Utilities.handle_argument(message)
                        target = Utilities.get_user_by_name(username)

                        if target is None:
                            connection.sendall("Error:?\n".encode())
                        else:
                            client.logger.info(f"Sent ping to {target.name} from {client.name}")
                            client.send(f"SentPing:{target.name}")
                            target.send(f"ReceivedPing:{client.name}")
                    case "Fetch":
                        result = Utilities.get_all_user_names_raw()
                        client.logger.info(f"Fetched all users: {result}")
                        client.send(f"Users:{result}")
                    case "Exit":
                        client.send_then_disconnect("Bye:?")
                        return
                    case "Name":
                        pass
                    case _:
                        client.logger.warning(f"Unknown command: {message}")
                        connection.sendall("Error:?\n".encode())

            else:
                client.logger.warning(f"Gracefully disconnecting {client.name}")
                client.close_connection()
                return
        except Exception as e:
            client.logger.error(f"Force disconnecting {client.name}, due to: {e.__str__()}")
            client.close_connection()
            return


while True:
    conn, addr = server.accept()

    user = Client(None, addr, conn)
    client_list.append(user)

    thread = threading.Thread(target=client_thread, args=(user,), name=f"Client: {addr[0]}")
    user.register_thread(thread)
    user.thread.start()

conn.close()
server.close()
