import socket
import threading
import sys
import time

from server import Server
from client import Client
from gui_window import ChatWindow
from message import Message
from gui_login import LoginWindow


def receive_message(msg: Message):
    print(f"Message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)


credentials = {"_PORT_": None, "_RECEIVER_PORT_": None, "_PASSWORD_": None}


def login(input: dict):
    global credentials
    for key in input:
        credentials[key] = input[key]


login_window = LoginWindow()
login_window.subscribe_confirm(login)

login_window.run()
login_window.close()

receive_port = int(credentials["_PORT_"])
user_id = receive_port
dest_port = int(credentials["_RECEIVER_PORT_"])

password = credentials["_PASSWORD_"]

serv = Server(receive_port, user_id, password)
serv.subscribe_message_received(receive_message)

server_thread = threading.Thread(target=serv.start)
server_thread.start()

time.sleep(0.1)
clie = Client(user_id, socket.gethostname(), dest_port, password)
clie.start()

# Run GUI
window = ChatWindow(user_id)
window.subscribe_message_send(clie.send_text)

window.run()
window.close()

# Close connections
clie.stop()
serv.stop()
print("Stopped all services")
