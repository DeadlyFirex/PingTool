import loguru
import socket
import argparse

from utils.helpers import (handle_message, get_client_by_name, get_all_clients,
                           perform_logging, load_config, clean_message, verify_client_name)
from utils.__init__ import TRACE, INFO, WARNING, ERROR
from models.client import Client

from os.path import abspath, dirname, join
from secrets import token_hex
from json import dumps
from typing import List
from concurrent.futures import ThreadPoolExecutor

# Setup variables
client_list: List[Client] = []
app_id: str = token_hex(8)
secret_key: str = token_hex(16)
root_path: str = abspath(dirname(abspath(__file__)))
cfg_path: str = join(root_path, "config.json")

# Load config / logging
cfg: dict = load_config(cfg_path)
app_config, app_settings, app_logging = (
    cfg.get("application"), cfg.get("settings"), cfg.get("logging"))
app_logger: int = loguru.logger.add(
    sink=app_logging.get("path"),
    level=app_logging.get("level"),
    rotation=app_logging.get("rotation"),
    compression=app_logging.get("compression")
)

# Setup command line arguments
parser = argparse.ArgumentParser(description=app_config["name"])
parser.add_argument('--host', type=str, help='The host to bind the server to')
parser.add_argument('--port', type=int, help='The port number to bind the server to')
args = parser.parse_args()

# Setup threading and server
thread_pool = ThreadPoolExecutor(thread_name_prefix="Clients-", max_workers=app_settings["max_workers"])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host: str = args.host if args.host else socket.gethostbyname(socket.gethostname())
port: int = args.port if args.port else 12500

loguru.logger.info(f"Booting up server on {host}:{port}")
loguru.logger.info(f"Identifier: ({app_id})")
loguru.logger.info(f"Secret: ({secret_key})")
server.bind((host, port))
server.listen(15)


@perform_logging(TRACE.name, "Created new client thread")
def client_thread(client: Client):
    client.send(f"Connected:{dumps(cfg)}")

    command, argument = handle_message(
        clean_message(
            client.connection.recv(2048)
        ))

    message, successful = verify_client_name(client_list, (app_settings['username_min_length'],
                                                           app_settings['username_max_length'],), command, argument)
    if not successful:
        client.log(f"Kicking user for bad verification", ERROR.name)
        client.send_then_disconnect(message)
        return
    client.send(message)

    client.name = argument
    client.log(f"Verified user as: {client.name}", INFO.name)

    while True:
        try:
            command, argument = handle_message(
                clean_message(
                    client.connection.recv(2048)
                ))

            match command:
                case "Ping":
                    target = get_client_by_name(client_list, argument)

                    if target is None:
                        client.send("Error:?")
                    else:
                        client.log(f"Sent ping to {target.name} from {client.name}", INFO.name)
                        client.send(f"S-Ping:{target.name}")
                        target.send(f"X-Ping:{client.name}")
                case "Fetch":
                    client.log(f"Fetched all users", INFO.name)
                    client.send(f"Users:{get_all_clients(client_list, True)}")
                case "Login":
                    if argument == secret_key:
                        client.admin = True
                        client.log(f"Successfully logged in as admin", INFO.name)
                        client.send(f"Login:True")
                    else:
                        client.log(f"Failed to login as admin", WARNING.name)
                        client.send(f"Error:?")
                case "Settings":
                    client.log(f"Fetched settings", INFO.name)
                    client.send(f"Settings:{dumps(cfg)}")
                case "Id":
                    client.log(f"Fetched server id", INFO.name)
                    client.send(f"Id:{app_id}")
                case "Exit":
                    client.send_then_disconnect("Bye:?")
                    return
                case "Name":
                    client.log(f"Fetched name of {argument}", INFO.name)
                    client.send(f"Name:{client.name}")
                case _:
                    client.log(f"Unknown command: {command or 'none'}", WARNING.name)
                    client.send("Error:?")

        except Exception as e:
            client.close_connection()
            loguru.logger.warning(f"Manually disconnecting {client.name or 'undefined'} for:"
                                  f" {e or 'no reason specified'}")
            if client in client_list:
                client_list.remove(client)
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
