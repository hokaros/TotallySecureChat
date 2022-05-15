import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable
from message import Message
from encryption import MessageEncryptor


class Client:
    def __init__(self, self_id, server_ip, server_port, session_key):
        self.self_id = self_id
        self.server_ip = server_ip
        self.server_port = server_port
        self.__socket = None

        self.__msg_encryptor = MessageEncryptor(session_key)

        self.__should_stop = ThreadSafeVariable(False)

        self.__on_message_sent = []

    def subscribe_message_sent(self, callback: Callable[[str], None]):
        self.__on_message_sent.append(callback)

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.server_ip, self.server_port))

        print(f"Client connected to {self.server_ip}:{self.server_port}")

    def send(self, msg: str):
        text_msg = Message.text_message(self.self_id, msg)
        text_msg.body = self.__msg_encryptor.encrypt(text_msg.body)

        bytes = text_msg.to_bytes()
        self.__socket.send(bytes)

        self.__invoke_message_sent(msg)

    def stop(self):
        self.__socket.close()
        self.__should_stop.set(True)
        print(f"Client disconnected")

    def __invoke_message_sent(self, msg: str):
        for callback in self.__on_message_sent:
            callback(msg)
