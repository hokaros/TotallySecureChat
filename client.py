import socket

from thread_utilities import ThreadSafeVariable


class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.__should_stop = ThreadSafeVariable(False)

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.server_ip, self.server_port))

        print(f"Client connected to {self.server_ip}:{self.server_port}")
        while True:
            msg = sock.recv(256)
            if msg != b'':
                print(msg)

            if self.__should_stop.get():
                break

        sock.close()
        print(f"Client disconnected")

    def stop(self):
        self.__should_stop.set(True)
