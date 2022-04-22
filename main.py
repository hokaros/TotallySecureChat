import socket
import time
import threading

from server import Server
from client import Client


port = 8080
serv = Server(port)
clie = Client(socket.gethostname(), port)

server_thread = threading.Thread(target=serv.start)
server_thread.start()

clie.start()  # main thread in the client

serv.stop()
print("Stopped all services")
