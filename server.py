import socket
import threading
import loguru

from sys import argv
from typing import Union
from assets.__init__ import *
from json import load, dumps
from secrets import token_hex
from concurrent.futures import ThreadPoolExecutor
from os.path import abspath, dirname, join

server_id = token_hex(8)
root_path = abspath(dirname(abspath(__file__)))
config_path = join(root_path, "config.json")
client_list = []


def perform_logging(level: str | int, message: str | None) -> callable:
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            loguru.logger.log(level, message or "no message")
            return f(*args, **kwargs)
        return wrapped_f
    return wrap


@perform_logging(TRACE.name, "Loading config.json")
def load_config(path: str) -> tuple[dict, dict]:
    with (open(path, "r")) as file:
        cfg_raw = load(file)
        cfg_app = cfg_raw["application"]
        cfg_settings = cfg_raw["settings"]
    return cfg_app, cfg_settings


config = load_config(config_path)[0]
settings = load_config(config_path)[1]
thread_pool = ThreadPoolExecutor(thread_name_prefix="Clients-",
                                 max_workers=settings["max_workers"])


class Client:
    @perform_logging(TRACE.name, "Creating user")
    def __init__(self, name: Union[str, None], address: tuple, connection: socket.socket):
        self.name: Union[str, None] = name
        self.address: tuple = address
        self.connection: socket.socket = connection
        self.thread: Union[threading.Thread, None] = None

    @perform_logging(TRACE.name, "Sending message")
    def send(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    @perform_logging(TRACE.name, "Sending message, then disconnecting")
    def send_then_disconnect(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.close_connection()

    @perform_logging(TRACE.name, "Verifying user")
    def verify(self, name: str):
        if name.__len__() > 25:
            self.send_then_disconnect("Error:?")
        self.name = name.split(":")[1].removesuffix("\n")

    @perform_logging(TRACE.name, "Disconnecting user")
    def close_connection(self, reason: Union[str, None] = None):
        loguru.logger.warning(f"Manually disconnecting {self.name} for: {reason or 'no reason specified'}")
        if self in client_list:
            client_list.remove(self)
        self.connection.close()

    @perform_logging(TRACE.name, "Registering thread to client")
    def register_thread(self, thread_address: threading.Thread):
        self.thread = thread_address

    @perform_logging(TRACE.name, "Logging message")
    def log(self, message: str | None, level: str | int = DEBUG.name):
        loguru.logger.log(level, message)


class Utilities:
    @staticmethod
    @perform_logging(TRACE.name, "Fetching all users")
    def get_all_user_names():
        result = list()

        for client in client_list:
            if client.name is None:
                continue
            result.append(client.name)
        return result or None

    @staticmethod
    @perform_logging(TRACE.name, "Raw-fetching all users")
    def get_all_user_names_raw():
        result = str()

        for client in client_list:
            if client.name is None:
                continue
            if result == str():
                result = result.__add__(client.name)
            else:
                result = result.__add__(f",{client.name}")

        return result or None

    @staticmethod
    @perform_logging(TRACE.name, "Fetching user by name")
    def get_user_by_name(name: str):
        for client in client_list:
            if client.name == name:
                return client
        return None

    @staticmethod
    @perform_logging(TRACE.name, "Fetching user by address")
    def get_user_by_address(address: str):
        for client in client_list:
            if client.address == address:
                return client
        return None

    @staticmethod
    @perform_logging(TRACE.name, "Parsing argument")
    def handle_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[1].removesuffix("\n")

    @staticmethod
    @perform_logging(TRACE.name, "Parsing command")
    def strip_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[0].removesuffix("\n")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

file_logger = loguru.logger.add(
    sink="logs/main.log",
    level="TRACE",
    rotation="15MB",
    compression="zip"
)
json_logger = loguru.logger.add(
    sink="logs/main.json",
    level="TRACE",
    serialize=True,
    rotation="20MB",
    compression="zip"
)
client_list = list()

try:
    ip_address = str(argv[1])
    port = int(argv[2])
except IndexError:
    ip_address = socket.gethostbyname(socket.gethostname())
    port = 5001

loguru.logger.info(f"Booting up server on {ip_address}:{port}")
server.bind((ip_address, port))
server.listen(15)


@perform_logging(TRACE.name, "Created new client thread")
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
                        client.log(f"Kicking user for bad verification", ERROR.name)
                        client.send_then_disconnect("Error:?")
                        return
                    name = Utilities.handle_argument(message)
                    if Utilities.get_user_by_name(name) is not None:
                        client.log(f"Kicking user for existing name", ERROR.name)
                        client.send_then_disconnect("Error:Name")
                        return
                    if name is None or name == "":
                        client.log(f"Kicking user for bad naming", ERROR.name)
                        client.send_then_disconnect("Error:?")
                        return
                    if not settings["username_min_length"] < name.__len__() < settings["username_max_length"]:
                        client.send_then_disconnect(f"Error:{settings['username_min_length']}/"
                                                    f"{settings['username_max_length']}={name.__len__()}")
                    client.name = name
                    client.log(f"Verified user as: {client.name}", INFO.name)
                    client.send(f"Verified:{client.name}")

                match Utilities.strip_argument(message):
                    case "Ping":
                        username = Utilities.handle_argument(message)
                        target = Utilities.get_user_by_name(username)

                        if target is None:
                            connection.sendall("Error:?\n".encode())
                        else:
                            client.log(f"Sent ping to {target.name} from {client.name}", INFO.name)
                            client.send(f"S-Ping:{target.name}")
                            target.send(f"X-Ping:{client.name}")
                    case "Fetch":
                        result = Utilities.get_all_user_names_raw()
                        client.log(f"Fetched all users: {result}", INFO.name)
                        client.send(f"Users:{result}")
                    case "Settings":
                        client.log(f"Fetched settings", INFO.name)
                        client.send(f"Settings:{dumps(config)}")
                    case "Id":
                        client.log(f"Fetched server id", INFO.name)
                        client.send(f"Id:{server_id}")
                    case "Exit":
                        client.send_then_disconnect("Bye:?")
                        return
                    case "Name":
                        pass
                    case _:
                        client.log(f"Unknown command: {message}", WARNING.name)
                        connection.sendall("Error:?\n".encode())

            else:
                client.close_connection("gracefully disconnecting")
                return
        except Exception as e:
            client.close_connection(f"forcefully disconnecting, {e.__str__()}")
            return


while True:
    try:
        conn, addr = server.accept()

        user = Client(None, addr, conn)
        client_list.append(user)

        t = thread_pool.submit(client_thread, user)
        user.register_thread(t)
    except KeyboardInterrupt:
        server.close()
        thread_pool.shutdown(wait=False)
        exit(0)
