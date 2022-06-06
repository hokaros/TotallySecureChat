import socket
from typing import Callable

from thread_utilities import ThreadSafeVariable
from message import Message
from encryption import MessageEncryptor
from Crypto.Cipher import AES
from logging import Log


class Client:
    def __init__(self, self_id: int, server_ip, server_port, password):
        self.self_id = self_id
        self.server_ip = server_ip
        self.server_port = server_port
        self.__socket = None

        self.__msg_encryptor = MessageEncryptor(str(self_id), password)

        self.__should_stop = ThreadSafeVariable(False)

        self.__on_message_sent = []
        self.__on_file_sent = []
        self.__on_file_transfer_started = []
        self.__on_file_transfer_progress = []

    def subscribe_message_sent(self, callback: Callable[[str], None]):
        self.__on_message_sent.append(callback)


    def subscribe_file_sent(self, callback: Callable[[str], None]):
        self.__on_file_sent.append(callback)

    def subscribe_file_transfer_started(self, callback: Callable[[], None]):
        self.__on_file_transfer_started.append(callback)

    def subscribe_file_transfer_progress(self, callback: Callable[[int], None]):
        self.__on_file_transfer_progress.append(callback)

    def use_ecb(self):
        self.__msg_encryptor.use_ecb()

    def use_cbc(self):
        self.__msg_encryptor.use_cbc()

    def set_cipher_mode(self, mode):
        if mode == AES.MODE_ECB:
            self.__msg_encryptor.use_ecb()
        elif mode == AES.MODE_CBC:
            self.__msg_encryptor.use_cbc()

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"Connecting to {self.server_ip}:{self.server_port}...")
        while True:
            if self.__should_stop.get():
                return

            try:
                self.__socket.connect((self.server_ip, self.server_port))
                Log.log(f"Client connected to {self.server_ip}:{self.server_port}")
                break
            except ConnectionRefusedError:
                pass  # Retry immediately

        self.__send_public_key()

    def stop(self):
        self.__socket.close()
        self.__should_stop.set(True)
        Log.log(f"Client disconnected")

    def send_text(self, msg: str):
        self.__send_session_key()

        text_msg = Message.text_message(self.self_id, msg)
        self.__send(text_msg)

        self.__invoke_message_sent(msg)

    def send_file(self, filepath: str):
        self.__send_session_key()

        filename_str = filepath.split('/')[-1]
        filename = bytearray(filename_str, "utf-8")

        with open(filepath, 'rb') as f:
            content = f.read()

            full_segments_n = len(content)//Message.file_message_len()
            progress = 0

            file_name_msg = Message.file_name_message(self.self_id, filename, segments_count=full_segments_n+1)
            self.__send(file_name_msg)
            self.__invoke_file_sent(file_name_msg)

            self.__invoke_file_transfer_started()
            for segment in range(full_segments_n):
                msg_content = content[segment*Message.file_message_len():(segment+1)*Message.file_message_len()]

                Log.log(f"segment {segment}: {msg_content}")

                file_msg = Message.file_message(self.self_id, msg_content)
                self.__send(file_msg)
                progress += 1
                self.__invoke_file_transfer_progress(progress*100//(full_segments_n + 1))

            msg_content = content[full_segments_n*Message.file_message_len():]
            if len(msg_content) > 0:

                Log.log(f"last segment: {msg_content}")

                file_msg = Message.file_message(self.self_id, msg_content)
                self.__send(file_msg)
            self.__invoke_file_transfer_progress(100)

    def __send(self, msg: Message):
        self.__msg_encryptor.encrypt(msg)
        self.__socket.send(msg.to_bytes())

    def __send_public_key(self):
        key_bytes = self.__msg_encryptor.my_public_key.export_key()
        key_msg = Message.public_key(self.self_id, bytearray(key_bytes))
        self.__send(key_msg)
        Log.log(f"Public key sent")

    def __send_session_key(self):
        session_key = MessageEncryptor.generate_session_key()

        receiver_id = str(self.server_port)
        msg = Message.session_key(self.self_id, bytearray(session_key), receiver_id)
        self.__send(msg)
        Log.log(f"Sent session key: {session_key}")

        self.__msg_encryptor.session_key = session_key

    def __invoke_message_sent(self, msg: str):
        for callback in self.__on_message_sent:
            callback(msg)

    def __invoke_file_sent(self, msg: str):
        for callback in self.__on_file_sent:
            callback(msg)

    def __invoke_file_transfer_started(self):
        for callback in self.__on_file_transfer_started:
            callback()

    def __invoke_file_transfer_progress(self, progress: int):
        for callback in self.__on_file_transfer_progress:
            callback(progress)
