from utils.__init__ import TRACE
from utils.helpers import clean_message, perform_logging

from socket import socket
from typing import Union
from json import loads


class Connection:
    """
    A class to represent a connection to a server
    """
    @perform_logging(TRACE.name, "Initializing new connection")
    def __init__(self, name: Union[str, None], address: tuple, connection: socket) -> None:
        """
        Initialize a connection
        :param name: Name of connection
        :param address: Address to host
        :param connection: Socket connection
        """
        self.name: Union[str, None] = name
        self.address: tuple = address
        self.connection: socket = connection

        connection.connect(address)
        self.config: Union[dict, None] = loads(
            clean_message(self.connection.recv(2048))
            .removeprefix("Connected:")
        )

    @perform_logging(TRACE.name, "Sending message from connection")
    def send(self, message: str) -> None:
        """
        Send a message to the client.
        :param message: Message to send
        :return: null
        """
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    @perform_logging(TRACE.name, "Sending message from connection, then disconnecting")
    def send_then_disconnect(self, message: str) -> None:
        """
        Send a message to the client, then disconnect.
        :param message: Message to send
        :return: null
        """
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.disconnect()

    @perform_logging(TRACE.name, "Disconnecting connection")
    def disconnect(self) -> None:
        """
        Remove and disconnect the "connection".
        :return: null
        """
        self.connection.close()
