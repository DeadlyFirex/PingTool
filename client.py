import socket
import loguru

from playsound import playsound
from select import select
from sys import argv, stdin, stdout
from typing import Union
from assets.__init__ import *


class Connection:
    def __init__(self, name: Union[str, None], address: tuple, connection: socket.socket):
        self.name: Union[str, None] = name
        self.address: tuple = address
        self.connection: socket.socket = connection

        connection.connect(address)

    def send(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    def send_then_disconnect(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.disconnect()

    def verify(self, name: str):
        if name.__len__() > 25:
            raise ValueError("Name too long")
        self.name = name
        self.send(f"Name:{name}")

    def disconnect(self, reason: Union[str, None] = None):
        loguru.logger.warning(f"Manually disconnecting {self.name} for: {reason or 'no reason specified'}")
        self.connection.close()

    def log(self, message: Union[str, None], level: Union[str, int] = DEBUG.name):
        loguru.logger.log(level, message)

    @staticmethod
    def handle_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[1].removesuffix("\n")

    @staticmethod
    def strip_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[0].removesuffix("\n")


conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

file_logger = loguru.logger.add(
    sink="logs/client.log",
    level="TRACE",
    rotation="15MB",
    compression="zip"
)

input_list = [stdin, conn]

try:
    HOST = str(argv[1])
    PORT = int(argv[2])
except IndexError:
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5001

loguru.logger.info(f"Booting client, setting to connect to {HOST}:{PORT}")

try:
    connection = Connection(None, (HOST, PORT), conn)
    connection.verify("Test")

    data = conn.recv(10024).decode('utf-8').removeprefix('\n').removesuffix('\n')

    if data.__contains__("Verified"):
        loguru.logger.success(f"Successfully verified using name: {connection.name}")

    while True:
        read_sockets, write_socket, error_socket = select(input_list, [], [])

        for socks in read_sockets:
            if socks == conn:
                message = socks.recv(2048).decode('utf-8').removeprefix('\n').removesuffix('\n')
                print(f"<Server> {message}")

                if message.__contains__("X-Ping"):
                    playsound("assets/beep.mp3")
            else:
                message = stdin.readline()
                connection.send(message)
                stdout.write(f"<Client> {message}")
                stdout.flush()

except KeyboardInterrupt:
    connection.disconnect()
    exit(0)
