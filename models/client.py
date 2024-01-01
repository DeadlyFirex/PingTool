import loguru

from socket import socket
from threading import Thread

from assets.__init__ import *
from utils.helpers import perform_logging, client_list


class Client:
    @perform_logging(TRACE.name, "Creating user")
    def __init__(self, name: str | None, address: tuple, connection: socket):
        self.name: str | None = name
        self.address: tuple = address
        self.connection: socket = connection
        self.thread: Thread | None = None

    @perform_logging(TRACE.name, "Sending message")
    def send(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))

    @perform_logging(TRACE.name, "Sending message, then disconnecting")
    def send_then_disconnect(self, message: str):
        self.connection.sendall(message.__add__("\n").encode("utf-8"))
        self.close_connection()

    @perform_logging(TRACE.name, "Verifying user")
    def verify(self, name: str):
        self.name = name.split(":")[1].removesuffix("\n")

    @perform_logging(TRACE.name, "Disconnecting user")
    def close_connection(self, reason: str | None = None):
        loguru.logger.warning(f"Manually disconnecting {self.name or 'undefined'} for:"
                              f" {reason or 'no reason specified'}")
        if self in client_list:
            client_list.remove(self)
        self.connection.close()

    @perform_logging(TRACE.name, "Registering thread to client")
    def register_thread(self, thread_address: Thread):
        self.thread = thread_address

    @perform_logging(TRACE.name, "Logging message")
    def log(self, message: str | None, level: str | int = DEBUG.name):
        loguru.logger.log(level, message)
