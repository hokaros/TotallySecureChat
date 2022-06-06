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


def receive_message(msg: Message):
    print(f"Message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)


def choose_encryption_mode() -> AES.MODE_CBC | AES.MODE_ECB:
    while True:
        selected_mode = input(f"Choose encryption mode (ECB or CBC):")

        if selected_mode.lower() == "ecb":
            return AES.MODE_ECB
        elif selected_mode.lower() == "cbc":
            return AES.MODE_CBC

        print("Unrecognised encryption mode")


def receive_file_name(msg: Message):
    print(f"File message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)
    filewri.create_file(msg.stringbody())


def receive_file(msg: Message):
    print(f"File message content received from user {msg.sender_id}: {msg.stringbody()}")
    filewri.write(msg.body)


receive_port = int((input("Receiving port: ")))
user_id = receive_port

username = str(user_id)
password = input("Password: ")
dest_port = int(input("Target port: "))
encryption_mode = choose_encryption_mode()

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
clie.set_cipher_mode(encryption_mode)

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
