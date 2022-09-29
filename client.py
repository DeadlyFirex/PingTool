import datetime
import socket
import loguru

from sys import argv
from typing import Union
from assets.__init__ import *


def PerformLogging(level: Union[str, int], message: Union[str, None]):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            loguru.logger.log(level, message or "no message")
            return f(*args, **kwargs)
        return wrapped_f
    return wrap


class Connection:
    @PerformLogging(TRACE.name, "Creating user")
    def __init__(self, name: Union[str, None], address: tuple, connection: socket.socket):
        self.name: Union[str, None] = name
        self.address: tuple = address
        self.connection: socket.socket = connection

        connection.connect(address)

    @PerformLogging(TRACE.name, "Sending message")
    def send(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    @PerformLogging(TRACE.name, "Sending message, then disconnecting")
    def send_then_disconnect(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.disconnect()

    @PerformLogging(TRACE.name, "Verifying user")
    def verify(self, name: str):
        if name.__len__() > 25:
            raise ValueError("Name too long")
        self.name = name
        self.send(f"Name:{name}")

    @PerformLogging(TRACE.name, "Disconnecting user")
    def disconnect(self, reason: Union[str, None] = None):
        loguru.logger.warning(f"Manually disconnecting {self.name} for: {reason or 'no reason specified'}")
        self.connection.close()

    @PerformLogging(TRACE.name, "Logging message")
    def log(self, message: Union[str, None], level: Union[str, int] = DEBUG.name):
        loguru.logger.log(level, message)

    @staticmethod
    @PerformLogging(TRACE.name, "Parsing argument")
    def handle_argument(message: str, delimiter: str = ":"):
        return message.split(delimiter)[1].removesuffix("\n")

    @staticmethod
    @PerformLogging(TRACE.name, "Parsing command")
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
json_logger = loguru.logger.add(
    sink="logs/client.json",
    level="TRACE",
    serialize=True,
    rotation="20MB",
    compression="zip"
)

client_list = list()
client_last_fetched = datetime.datetime.now()

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

    while True:
        data = conn.recv(1024).decode('utf-8').removeprefix('\n').removesuffix('\n')
        print(f"RECEIVED: {data.__str__()}")
except KeyboardInterrupt:
        connection.disconnect()
        exit(0)
