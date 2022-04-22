import socket
import threading

from server import Server
from client import Client


# TODO: pobieranie adresów z bazy
receive_port = int((input("Podaj port odbierania: ")))
dest_port = int(input("Podaj port docelowy: "))

serv = Server(receive_port)
clie = Client(socket.gethostname(), dest_port)

server_thread = threading.Thread(target=serv.start)
server_thread.start()

input("Press enter to connect\n")
clie.start()  # main thread in the client

serv.stop()
print("Stopped all services")
