import socket

from thread_utilities import ThreadSafeVariable


class Server:
    def __init__(self, port: int):
        self.port = port
        self.__should_stop = ThreadSafeVariable(False)
        self.__socket = None

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
                    msg = connection.recv(256).decode("utf-8", "strict")
                    if msg != "":
                        print("Message received: ", msg)

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
