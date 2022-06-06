import socket
from typing import Callable
from Crypto.PublicKey import RSA

from thread_utilities import ThreadSafeVariable
from message import Message, MessageType
from encryption import MessageEncryptor
from logging import Log


class Server:
    def __init__(self, port: int, user_id: int, password):
        self.port = port
        self.__should_stop = ThreadSafeVariable(False)
        self.__socket = None

        self.__msg_encryptor = MessageEncryptor(str(user_id), password)
        self.__receive_buffer = bytearray()

        self.current_file_segments = 1
        self.received_segments = 0

        self.__on_message_received = []
        self.__on_file_name_received = []
        self.__on_file_received = []
        self.__on_file_transfer_started = []
        self.__on_file_transfer_progress = []

    def subscribe_message_received(self, callback: Callable[[Message], None]):
        self.__on_message_received.append(callback)

    def subscribe_file_received(self, callback: Callable[[Message], None]):
        self.__on_file_received.append(callback)

    def subscribe_file_name_received(self, callback: Callable[[Message], None]):
        self.__on_file_name_received.append(callback)

    def subscribe_file_transfer_started(self, callback: Callable[[], None]):
        self.__on_file_transfer_started.append(callback)

    def subscribe_file_transfer_progress(self, callback: Callable[[int], None]):
        self.__on_file_transfer_progress.append(callback)

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.__socket.bind((host, self.port))

        self.__socket.listen()
        Log.log(f"Server listening on {host}:{self.port}")

        while True:
            try:
                connection, addr = self.__socket.accept()
                Log.log(f"Got connection from {addr}")
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
        Log.log(f"Server stopped")

    def stop(self):
        self.__socket.close()
        self.__should_stop.set(True)

    def __on_bytes_received(self, bytes: bytes):
        if len(bytes) == 0:
            return

        Log.log(f"Received {len(bytes)} bytes")
        self.__receive_buffer.extend(bytes)

        # Consume from the buffer
        messages, remaining_bytes = Message.multiple_from_bytes(self.__receive_buffer)
        for msg in messages:
            self.__receive_message(msg)

        self.__receive_buffer = remaining_bytes

    def __receive_message(self, msg: Message):
        try:
            self.__msg_encryptor.decrypt(msg)
        except ValueError:
            Log.log("Key incorrect or message corrupted")

        if msg.type == MessageType.TEXT_MESSAGE:
            self.__invoke_message_received(msg)
        elif msg.type == MessageType.SESSION_KEY:
            Log.log(f"New session key: {msg.body}")
            self.__msg_encryptor.session_key = msg.body
        elif msg.type == MessageType.FILE_NAME_MESSAGE:
            self.current_file_segments = msg.segments_count
            self.received_segments = 0
            Log.log(f"New file coming: {msg.body}")
            self.__invoke_file_name_received(msg)
            self.__invoke_file_transfer_started()
        elif msg.type == MessageType.FILE_MESSAGE:
            self.received_segments += 1
            self.__invoke_file_received(msg)
            self.__invoke_file_transfer_progress(self.received_segments*100//self.current_file_segments)
            Log.log(f"New file content: {msg.body}")
        elif msg.type == MessageType.PUBLIC_KEY:
            Log.log(f"Public key received from user {msg.sender_id}")
            key = RSA.import_key(msg.body)
            self.__msg_encryptor.pki.save_public_key(str(msg.sender_id), key)

    def __invoke_message_received(self, msg: Message):
        for callback in self.__on_message_received:
            callback(msg)

    def __invoke_file_received(self, file: Message):
        for callback in self.__on_file_received:
            callback(file)

    def __invoke_file_name_received(self, file: Message):
        for callback in self.__on_file_name_received:
            callback(file)

    def __invoke_file_transfer_started(self):
        for callback in self.__on_file_transfer_started:
            callback()

    def __invoke_file_transfer_progress(self, progress: int):
        for callback in self.__on_file_transfer_progress:
            callback(progress)
