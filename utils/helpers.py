import loguru

from utils.__init__ import TRACE

from json import load
from typing import List, Union, Tuple


def perform_logging(level: Union[str, int], message: Union[str, None]) -> callable:
    """
    Decorator to perform logging for a function. \n
    Perform logging for a function.
    :param level: Level of logging
    :param message: Message to log
    :return: callable
    """
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            # print(f"Performing logging for {f.__name__} with level {level} and message "
            #       f"{message} and args {args} and kwargs {kwargs}")
            loguru.logger.log(level, message or "no message")
            return f(*args, **kwargs)
        return wrapped_f
    return wrap


@perform_logging(TRACE.name, "Loading configuration")
def load_config(config_path: str) -> dict:
    """
    Load config from a file.
    :param config_path: Path to configuration
    :return: Configuration (dict)
    """
    with (open(config_path, "r")) as file:
        cfg_raw = load(file)
    return cfg_raw


@perform_logging(TRACE.name, "Cleaning message")
def clean_message(message: bytes) -> str:
    """
    Cleans a socket received message.
    :param message: Bytes from connection
    :return: Message (clean)
    """
    if message is None:
        return ":"
    return (message
            .decode("utf-8")
            .removeprefix("\n")
            .removesuffix("\n"))


@perform_logging(TRACE.name, "Parsing all clients to list")
def get_all_clients(client_list: List[object], return_raw: bool = False) -> Union[List[str], str]:
    """
    Parses a client list to a list of names, or formatted string.
    :param client_list: List of client names
    :param return_raw: Return joined string
    :return: List of client names, or formatted string
    """
    result = [
        client.name for client
        in client_list
        if client.name is not None
    ]

    if return_raw:
        return ",".join(result)
    return result


@perform_logging(TRACE.name, "Fetching client by name")
def get_client_by_name(client_list: List[object], client_name: str) -> Union[object, None]:
    """
    Fetches a client by name.
    :param client_list: List of clients
    :param client_name: Name of client
    :return: Client or None
    """
    for client in client_list:
        if client.name == client_name:
            return client
    return None


@perform_logging(TRACE.name, "Fetching client by address")
def get_client_by_address(client_list: List[object], client_address: str) -> Union[object, None]:
    """
    Fetches a client by address.
    :param client_list: List of clients
    :param client_address: Remote address of client
    :return: Client or None
    """
    for client in client_list:
        if client.address == client_address:
            return client
    return None


@perform_logging(TRACE.name, "Verifying client name")
def verify_client_name(client_list: List[object], min_max: Tuple[int, int], command: str, argument: str) -> Tuple[str, bool]:
    """
    Verifies if a client name is valid.
    :param client_list: List of clients
    :param min_max: Minimum and maximum length of name
    :param command: Command to verify
    :param argument: Argument to verify
    :return: Tuple; (message, successful?)
    """
    # Verify client
    if command != "Name" or argument in [None, ""]:
        return "Error:1", False
    elif get_client_by_name(client_list, argument) is not None:
        return "Error:2", False
    elif not min_max[0] < argument.__len__() < min_max[1]:
        return f"Error:{min_max[0]}/{min_max[1]}={argument.__len__()}", False
    else:
        return f"Verified:{argument}", True


@perform_logging(TRACE.name, "Parsing argument")
def handle_message(message: str, delimiter: str = ":") -> tuple[str, ...]:
    """
    Parses an argument from a message.
    :param message: Socket message
    :param delimiter: Delimiter to split by
    :return: Tuple of arguments
    """
    if message.__contains__(delimiter):
        return tuple(msg.removesuffix("\n") for msg in message.split(delimiter))
    return message, ""
