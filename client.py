import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable


class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.__socket = None

        self.__should_stop = ThreadSafeVariable(False)

        self.__on_message_sent = []

    def subscribe_message_sent(self, callback: Callable[[str], None]):
        self.__on_message_sent.append(callback)

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.server_ip, self.server_port))

        print(f"Client connected to {self.server_ip}:{self.server_port}")

    def send(self, msg):
        self.__socket.send(bytearray(msg.encode("utf-8")))
        self.__invoke_message_sent(msg)

    def stop(self):
        self.__socket.close()
        self.__should_stop.set(True)
        print(f"Client disconnected")

    def __invoke_message_sent(self, msg: str):
        for callback in self.__on_message_sent:
            callback(msg)
