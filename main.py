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
client_thread = threading.Thread(target=clie.start)
client_thread.start()
print("After starting")

time.sleep(1)
serv.stop()
clie.stop()
print("Stopped all services")
