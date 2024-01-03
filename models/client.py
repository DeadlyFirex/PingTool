import loguru

from utils.__init__ import DEBUG, TRACE
from utils.helpers import perform_logging

from socket import socket
from threading import Thread
from typing import Union


class Client:
    """
    Class represents a client connection.
    """
    @perform_logging(TRACE.name, "Creating new client")
    def __init__(self, name: Union[str, None], address: tuple, connection: socket) -> None:
        """
        Initialize a new client connection.
        :param name: Name of client
        :param address: IP Address of client
        :param connection: Socket connection
        """
        self.name: Union[str, None] = name
        self.address: tuple = address
        self.connection: socket = connection
        self.thread: Union[Thread, None] = None

    @perform_logging(TRACE.name, "Sending message to client")
    def send(self, message: str) -> None:
        """
        Send a message to the client.
        :param message: Message to send
        :return: null
        """
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    @perform_logging(TRACE.name, "Sending message to client, then disconnecting")
    def send_then_disconnect(self, message: str) -> None:
        """
        Send a message to the client, then disconnect.
        :param message: Message to send
        :return: null
        """
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.close_connection()

    @perform_logging(TRACE.name, "Disconnecting user")
    def close_connection(self) -> None:
        """
        Close the connection with the client.
        :return: null
        """
        self.connection.close()
        return

    @perform_logging(TRACE.name, "Registering thread to client")
    def register_thread(self, thread_address: Thread) -> None:
        """
        Register the thread to the client.
        :param thread_address: Thread to register
        :return: null
        """
        self.thread = thread_address

    @perform_logging(TRACE.name, "Logging message")
    def log(self, message: Union[str, None], level: Union[str, int] = DEBUG.name) -> None:
        """
        Log a message.
        :param message: Message to log
        :param level: Level of logging
        :return: null
        """
        loguru.logger.log(level, message)
