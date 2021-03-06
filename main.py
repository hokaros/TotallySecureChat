import os.path
import socket
import threading
import sys
import time

from server import Server
from client import Client
from gui_window import ChatWindow
from message import Message
from filewriter import FileWriter, UserDirectory
from Crypto.Cipher import AES
from gui_login import LoginWindow
from filewriter import FileWriter
from logging import Log


def receive_message(msg: Message):
    Log.log(f"Message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)


def choose_encryption_mode(client):
    if credentials["ecb"]:
        client.use_ecb()
    elif credentials["cbc"]:
        client.use_cbc()


def receive_file_name(msg: Message):
    Log.log(f"File message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)
    filewri.create_file(msg.stringbody())


def receive_file(msg: Message):
    Log.log(f"File message content received from user {msg.sender_id}: {msg.stringbody()}")
    filewri.write(msg.body)


def login(input: dict):
    global credentials
    for key in input:
        credentials[key] = input[key]


credentials = {"_PORT_": None, "_RECEIVER_PORT_": None, "_PASSWORD_": None, "_ENC_MODE_": None}

Log.enabled = False

login_window = LoginWindow()
login_window.subscribe_confirm(login)

login_window.run()
login_window.close()

receive_port = int(credentials["_PORT_"])
user_id = receive_port
dest_port = int(credentials["_RECEIVER_PORT_"])

password = credentials["_PASSWORD_"]
username = str(user_id)

UserDirectory.main = UserDirectory(user_id)
filewri = FileWriter(os.path.join(UserDirectory.main.directory, "downloaded"))

# Start server and client
serv = Server(receive_port, user_id, password)
serv.subscribe_message_received(receive_message)
serv.subscribe_file_name_received(receive_file_name)
serv.subscribe_file_received(receive_file)

server_thread = threading.Thread(target=serv.start)
server_thread.start()

time.sleep(0.1)
clie = Client(user_id, socket.gethostname(), dest_port, password)
choose_encryption_mode(clie)
clie.start()

filewri = FileWriter(os.path.join("downloaded", username))



# Run GUI
window = ChatWindow(user_id)
window.subscribe_message_send(clie.send_text)
window.subscribe_file_send(clie.send_file)
clie.subscribe_file_transfer_started(window.start_progress_bar)
clie.subscribe_file_transfer_progress(window.proceed_progress_bar)
serv.subscribe_file_transfer_started(window.start_progress_bar)
serv.subscribe_file_transfer_progress(window.proceed_progress_bar)

window.run()
window.close()

# Close connections
clie.stop()
serv.stop()
Log.log("Stopped all services")
