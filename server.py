import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable
from message import Message


class Server:
    def __init__(self, port: int):
        self.port = port
        self.__should_stop = ThreadSafeVariable(False)
        self.__socket = None

        self.__on_message_received = []

    def subscribe_message_received(self, callback: Callable[[Message], None]):
        self.__on_message_received.append(callback)

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.__socket.bind((host, self.port))

        self.__socket.listen()
        print(f"Server listening on {host}:{self.port}")

        while True:
            try:
                connection, addr = self.__socket.accept()
                print("Got connection from", addr)
                while True:
                    bytes = connection.recv(256)
                    if len(bytes) != 0:
                        msg = Message.from_bytes(bytes)
                        self.__invoke_message_received(msg)

                    if self.__should_stop.get():
                        break

                connection.close()
            except Exception:
                break

            if self.__should_stop.get():
                break

        self.__socket.close()
        print(f"Server stopped")

    def stop(self):
        self.__socket.close()
        self.__should_stop.set(True)

    def __invoke_message_received(self, msg: Message):
        for callback in self.__on_message_received:
            callback(msg)
