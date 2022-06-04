import os.path
import socket
import threading
import sys
import time

from server import Server
from client import Client
from gui_window import ChatWindow
from message import Message
from filewriter import FileWriter


def receive_message(msg: Message):
    print(f"Message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)


def receive_file_name(msg: Message):
    print(f"File message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)
    filewri.create_file(msg.stringbody())


def receive_file(msg: Message):
    print(f"File message content received from user {msg.sender_id}: {msg.stringbody()}")
    filewri.write(msg.body)


# TODO: get addresses from a database
receive_port = int((input("Receiving port: ")))
# TODO: get user id from a database
user_id = receive_port

# TODO: get password from the user
username = str(user_id)
password = str(user_id)

serv = Server(receive_port, username, password)
serv.subscribe_message_received(receive_message)
serv.subscribe_file_name_received(receive_file_name)
serv.subscribe_file_received(receive_file)

server_thread = threading.Thread(target=serv.start)
server_thread.start()

time.sleep(0.1)
dest_port = int(input("Target port: "))
clie = Client(user_id, socket.gethostname(), dest_port, username, password)
filewri = FileWriter(os.path.join("downloaded", username))
input("Press enter to connect\n")
clie.start()

# Run GUI
window = ChatWindow(user_id)
window.subscribe_message_send(clie.send_text)
window.subscribe_file_send(clie.send_file)

window.run()
window.close()


# Close connections
clie.stop()
serv.stop()
print("Stopped all services")
