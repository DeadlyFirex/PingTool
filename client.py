import socket
import loguru
import argparse

from select import select
from secrets import token_hex
from sys import stdin, stdout
from typing import Union
from json import loads

try:
    from playsound import playsound
except ImportError:
    loguru.logger.warning("Failed to import playsound, will not play sound on ping")
    playsound = None


class Connection:
    def __init__(self, name: str | None, address: tuple, connection: socket.socket):
        self.name: str | None = name
        self.address: tuple = address
        self.connection: socket.socket = connection

        connection.connect(address)
        self.config: dict | None = loads(self.connection.recv(2048)
                                         .decode("utf-8")
                                         .removeprefix("\n")
                                         .removesuffix("\n")
                                         .removeprefix("Connected:"))

    def send(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    def send_then_disconnect(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.disconnect()

    def verify(self, name: str):
        min_len, max_len = (self.config.get("settings").get("username_min_length"),
                            self.config.get("settings").get("username_max_length"))

        if name is None or name == "":
            raise ValueError("Name cannot be empty")
        if min_len > name.__len__() > max_len:
            raise ValueError("Name length is invalid")
        self.name = name
        self.send(f"Name:{name}")

    def get_config(self):
        pass

    def disconnect(self, reason: Union[str, None] = None):
        loguru.logger.warning(f"Manually disconnecting {self.name} for: {reason or 'no reason specified'}")
        self.connection.close()

    @staticmethod
    def handle_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[1].removesuffix("\n")

    @staticmethod
    def strip_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[0].removesuffix("\n")


# Setup logger
app_logger = loguru.logger.add(
    sink="logs/client.log",
    level="TRACE",
    rotation="15MB",
    compression="zip"
)

# Setup command line arguments
parser = argparse.ArgumentParser(description="Application to demonstrate PingTool servers")
parser.add_argument('--host', type=str, help='The host to bind the server to')
parser.add_argument('--port', type=int, help='The port number to bind the server to')
parser.add_argument('--name', type=str, help='The name to connect with')
parser.add_argument('--test', type=bool, help='Ignore input and attempt connecting')
args = parser.parse_args()

# Setup connection
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = args.host if args.host else socket.gethostbyname(socket.gethostname())
port = args.port if args.port else 12500
name = args.name if args.name else token_hex(6)
input_list = [stdin, conn]

loguru.logger.info(f"Booting client, setting to connect to {host}:{port}")

try:
    connection = Connection(None, (host, port), conn)
    connection.verify(name)

    data = conn.recv(10024).decode('utf-8').removeprefix('\n').removesuffix('\n')

    if data.__contains__("Verified"):
        loguru.logger.success(f"Successfully verified using name: {connection.name}")

    while True:
        if args.test:
            connection.send_then_disconnect("Fetch")
            exit(0)

        read_sockets, write_socket, error_socket = select(input_list, [], [])

        for socks in read_sockets:
            if socks == conn:
                message = socks.recv(2048).decode('utf-8').removeprefix('\n').removesuffix('\n')
                print(f"<Server> {message}")

                if message.__contains__("X-Ping"):
                    if playsound is None:
                        loguru.logger.success("Pinged!")
                    else: playsound("assets/beep.mp3")
            else:
                message = stdin.readline()
                connection.send(message)
                stdout.write(f"<Client> {message}")
                stdout.flush()

except KeyboardInterrupt:
    connection.disconnect()
    exit(0)
except ConnectionRefusedError:
    loguru.logger.error(f"Failed to connect to {host}:{port}")
    exit(1)
