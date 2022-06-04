import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable
from message import Message, MessageType
from encryption import MessageEncryptor


class Server:
    def __init__(self, port: int, username, password):
        self.port = port
        self.__should_stop = ThreadSafeVariable(False)
        self.__socket = None

        self.__msg_encryptor = MessageEncryptor(username, password)

        self.__on_message_received = []
        self.__on_file_name_received = []
        self.__on_file_received = []

    def subscribe_message_received(self, callback: Callable[[Message], None]):
        self.__on_message_received.append(callback)

    def subscribe_file_received(self, callback: Callable[[Message], None]):
        self.__on_file_received.append(callback)

    def subscribe_file_name_received(self, callback: Callable[[Message], None]):
        self.__on_file_name_received.append(callback)

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
        if len(bytes) == 0:
            return

        print(f"Received {len(bytes)} bytes")
        for msg in Message.multiple_from_bytes(bytes):
            self.__receive_message(msg)

    def __receive_message(self, msg: Message):
        try:
            self.__msg_encryptor.decrypt(msg)
        except ValueError:
            print("Key incorrect or message corrupted")
            return

        if msg.type == MessageType.TEXT_MESSAGE:
            self.__invoke_message_received(msg)
        elif msg.type == MessageType.SESSION_KEY:
            print("New session key: ", msg.body)
            self.__msg_encryptor.session_key = msg.body
        elif msg.type == MessageType.FILE_NAME_MESSAGE:
            print("New file coming: ", msg.body)
            self.__invoke_file_name_received(msg)
        elif msg.type == MessageType.FILE_MESSAGE:
            print("New file content: ", msg.body)
            self.__invoke_file_received(msg)

    def __invoke_message_received(self, msg: Message):
        for callback in self.__on_message_received:
            callback(msg)

    def __invoke_file_received(self, file: Message):
        for callback in self.__on_file_received:
            callback(file)

    def __invoke_file_name_received(self, file: Message):
        for callback in self.__on_file_name_received:
            callback(file)
