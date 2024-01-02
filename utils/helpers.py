import loguru

from assets.__init__ import *
from utils.singleton import Singleton

from json import load

client_list = []


def perform_logging(level: str | int, message: str | None) -> callable:
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            loguru.logger.log(level, message or "no message")
            return f(*args, **kwargs)
        return wrapped_f
    return wrap


def clean_message(message: bytes) -> str:
    """
    Cleans a socket received message.
    :param message: Bytes from connection
    :return: Message (clean)
    """
    return (message
            .decode("utf-8")
            .removeprefix("\n")
            .removesuffix("\n"))


@perform_logging(TRACE.name, "Loading config.json")
def load_config(path: str) -> dict:
    with (open(path, "r")) as file:
        cfg_raw = load(file)
    return cfg_raw


class Utils(metaclass=Singleton):
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
