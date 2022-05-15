import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable
from message import Message, MessageType
from encryption import MessageEncryptor
from Crypto.Random import get_random_bytes


class Client:
    def __init__(self, self_id, server_ip, server_port):
        self.self_id = self_id
        self.server_ip = server_ip
        self.server_port = server_port
        self.__socket = None

        self.__msg_encryptor = MessageEncryptor()
        self.__first_message = True  # tmp

        self.__should_stop = ThreadSafeVariable(False)

        self.__on_message_sent = []

    def subscribe_message_sent(self, callback: Callable[[str], None]):
        self.__on_message_sent.append(callback)

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.server_ip, self.server_port))

        print(f"Client connected to {self.server_ip}:{self.server_port}")

    def stop(self):
        self.__socket.close()
        self.__should_stop.set(True)
        print(f"Client disconnected")

    def send_text(self, msg: str):
        if self.__first_message:
            self.__send_session_key()
            self.__first_message = False

        text_msg = Message.text_message(self.self_id, msg)
        self.__send(text_msg)

        self.__invoke_message_sent(msg)

    def __send(self, msg: Message):
        self.__msg_encryptor.encrypt(msg)
        self.__socket.send(msg.to_bytes())

    def __send_session_key(self):
        session_key = MessageEncryptor.generate_session_key()

        msg = Message(self.self_id, MessageType.SESSION_KEY, bytearray(session_key))
        self.__send(msg)
        print("Sent session key: ", session_key)

        self.__msg_encryptor.session_key = session_key


    def __invoke_message_sent(self, msg: str):
        for callback in self.__on_message_sent:
            callback(msg)
