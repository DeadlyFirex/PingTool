import socket
import loguru
import argparse

from assets.__init__ import *
from utils.helpers import Utils, perform_logging, load_config, client_list
from models.client import Client

from json import dumps
from secrets import token_hex
from concurrent.futures import ThreadPoolExecutor
from os.path import abspath, dirname, join

# Setup variables
app_id = token_hex(8)
root_path = abspath(dirname(abspath(__file__)))
cfg_path = join(root_path, "config.json")

# Load config / logging
cfg = load_config(cfg_path)
app_config, app_settings, app_logging = (
    cfg.get("application"), cfg.get("settings"), cfg.get("logging"))
app_logger = loguru.logger.add(
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

host = args.host if args.host else socket.gethostbyname(socket.gethostname())
port = args.port if args.port else 12500


loguru.logger.info(f"Booting up server on {host}:{port}")
server.bind((host, port))
server.listen(15)


@perform_logging(TRACE.name, "Created new client thread")
def client_thread(client: Client):
    connection = client.connection
    client.send(f"Connected:{dumps(cfg)}")

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
                    name = Utils.handle_argument(message)
                    if Utils.get_user_by_name(name) is not None:
                        client.log(f"Kicking user for existing name", ERROR.name)
                        client.send_then_disconnect("Error:Name")
                        return
                    if name is None or name == "":
                        client.log(f"Kicking user for bad naming", ERROR.name)
                        client.send_then_disconnect("Error:?")
                        return
                    if not app_settings["username_min_length"] < name.__len__() < app_settings["username_max_length"]:
                        client.send_then_disconnect(f"Error:{app_settings['username_min_length']}/"
                                                    f"{app_settings['username_max_length']}={name.__len__()}")
                    client.name = name
                    client.log(f"Verified user as: {client.name}", INFO.name)
                    client.send(f"Verified:{client.name}")

                match Utils.strip_argument(message):
                    case "Ping":
                        username = Utils.handle_argument(message)
                        target = Utils.get_user_by_name(username)

                        if target is None:
                            connection.sendall("Error:?\n".encode())
                        else:
                            client.log(f"Sent ping to {target.name} from {client.name}", INFO.name)
                            client.send(f"S-Ping:{target.name}")
                            target.send(f"X-Ping:{client.name}")
                    case "Fetch":
                        result = Utils.get_all_user_names_raw()
                        client.log(f"Fetched all users", INFO.name)
                        client.send(f"Users:{result}")
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
