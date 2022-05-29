import socket
import threading
import sys
import time

from server import Server
from client import Client
from gui_window import ChatWindow
from message import Message


def receive_message(msg: Message):
    print(f"Message received from user {msg.sender_id}: {msg.stringbody()}")
    window.receive_message(msg.stringbody(), msg.sender_id)


receive_port = int((input("Receiving port: ")))
user_id = receive_port

password = input("Password: ")

serv = Server(receive_port, user_id, password)
serv.subscribe_message_received(receive_message)

server_thread = threading.Thread(target=serv.start)
server_thread.start()

time.sleep(0.1)
dest_port = int(input("Target port: "))
clie = Client(user_id, socket.gethostname(), dest_port, password)
input("Press enter to connect\n")
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

