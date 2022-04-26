import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable


class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.__should_stop = ThreadSafeVariable(False)

        self.__on_message_sent = []

    def subscribe_message_sent(self, callback: Callable[[str], None]):
        self.__on_message_sent.append(callback)

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.server_ip, self.server_port))

        print(f"Client connected to {self.server_ip}:{self.server_port}")
        print("[Type a Message to send it. Type \"quit\" to close]")
        while True:
            msg = input()
            if msg == "quit":
                break

            sock.send(bytearray(msg.encode("utf-8")))
            self.__invoke_message_sent(msg)

            if self.__should_stop.get():
                break

        sock.close()
        print(f"Client disconnected")

    def stop(self):
        self.__should_stop.set(True)

    def __invoke_message_sent(self, msg: str):
        for callback in self.__on_message_sent:
            callback(msg)
