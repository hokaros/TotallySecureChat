import socket
import threading
import sys
import time

from server import Server
from client import Client
from gui_window import ChatWindow


def receive_message(msg):
    window.receive_message(msg, 2)  # always assume sender id = 2


# TODO: get user id from a database
if len(sys.argv) > 1:
    user_id = int(sys.argv[1])
else:
    user_id = 1

# TODO: get addresses from a database
receive_port = int((input("Receiving port: ")))

serv = Server(receive_port)
serv.subscribe_message_received(receive_message)

server_thread = threading.Thread(target=serv.start)
server_thread.start()

time.sleep(0.1)
dest_port = int(input("Target port: "))
clie = Client(socket.gethostname(), dest_port)
input("Press enter to connect\n")
clie.start()

# Run GUI
window = ChatWindow(user_id)
window.subscribe_message_send(clie.send)

window.run()
window.close()


# Close connections
clie.stop()
serv.stop()
print("Stopped all services")

