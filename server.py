import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable
from message import Message, MessageType
from encryption import MessageEncryptor


class Server:
    def __init__(self, port: int, user_id: int, password):
        self.port = port
        self.__should_stop = ThreadSafeVariable(False)
        self.__socket = None

        self.__msg_encryptor = MessageEncryptor(str(user_id), password)

        self.__on_message_received = []

    def subscribe_message_received(self, callback: Callable[[Message], None]):
        self.__on_message_received.append(callback)

    def use_ecb(self):
        self.__msg_encryptor.use_ecb()

    def use_cbc(self):
        self.__msg_encryptor.use_cbc()

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
                    bytes = connection.recv(1024)
                    self.__on_bytes_received(bytes)

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

    def __on_bytes_received(self, bytes: bytes):
        print(f"Received {len(bytes)} bytes")
        if len(bytes) == 0:
            return

        msg = Message.from_bytes(bytes)
        try:
            self.__msg_encryptor.decrypt(msg)
        except ValueError:
            print("Key incorrect or message corrupted")

        if msg.type == MessageType.TEXT_MESSAGE:
            self.__invoke_message_received(msg)
        elif msg.type == MessageType.SESSION_KEY:
            print("New session key: ", msg.body)
            self.__msg_encryptor.session_key = msg.body

    def __invoke_message_received(self, msg: Message):
        for callback in self.__on_message_received:
            callback(msg)
