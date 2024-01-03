import socket
import loguru
import argparse

from models.connection import Connection
from utils.helpers import clean_message, handle_message

from select import select
from secrets import token_hex
from sys import stdin, stdout
from os.path import isfile

try:
    from playsound import playsound
except ImportError:
    loguru.logger.warning("Failed to import playsound, will not play sound on ping")
    playsound = None

# Setup logger
app_logger = loguru.logger.add(
    sink="logs/client.log",
    level="INFO",
    rotation="15MB",
    compression="zip"
)

# Setup command line arguments
parser = argparse.ArgumentParser(description="Application to demonstrate PingTool servers")
parser.add_argument('--host', type=str, help='The host to bind the server to')
parser.add_argument('--port', type=int, help='The port number to bind the server to')
parser.add_argument('--name', type=str, help='The name to connect with')
parser.add_argument('--file', type=str, help='Path to ping audio file')
parser.add_argument('--test', type=bool, help='Ignore input and attempt connecting')
args = parser.parse_args()

# Setup connection
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = args.host if args.host else socket.gethostbyname(socket.gethostname())
port = args.port if args.port else 12500
name = args.name if args.name else token_hex(6)
input_list = [stdin, conn]

if args.file is not None and not isfile(args.file):
    raise FileNotFoundError(f"File {args.file} does not exist")
loguru.logger.info(f"Booting client, setting to connect to {host}:{port}")

try:
    connection: Connection = Connection(None, (host, port), conn)
    min_len, max_len = (connection.config.get("settings").get("username_min_length"),
                        connection.config.get("settings").get("username_max_length"))

    if name in [None, ""]:
        raise ValueError("Name cannot be empty")
    if min_len > name.__len__() > max_len:
        raise ValueError("Name length is invalid")

    connection.send(f"Name:{name}")
    command, argument = handle_message(
        clean_message(
            conn.recv(2048)
        ))

    if command == "Verified":
        connection.name = name
        loguru.logger.success(f"Successfully verified using name: {connection.name}")
    else:
        loguru.logger.error(f"Failed to verify using name: {connection.name}")
        raise ConnectionError("Failed to verify")

    while True:
        if args.test:
            loguru.logger.info("Sending test message")
            connection.send_then_disconnect("Fetch:")
            exit(0)

        read_sockets, write_socket, error_socket = select(input_list, [], [])

        for socks in read_sockets:
            if socks == conn:
                command, argument = handle_message(
                    clean_message(
                        conn.recv(2048)
                    ))

                stdout.write(f"<Server> {command}:{argument}\n")

                if command == "X-Ping":
                    if playsound is None:
                        loguru.logger.success("Pinged!")
                    else:
                        playsound(args.file)
            else:
                message = stdin.readline()
                connection.send(message)
                stdout.write(f"<Client> {message}")
                stdout.flush()

except KeyboardInterrupt:
    loguru.logger.warning(f"Manually disconnecting")
    connection.disconnect()
    exit(0)
except ConnectionRefusedError:
    loguru.logger.error(f"Failed to connect to {host}:{port}")
    exit(1)
