from gui_window import *
import sys


def send_message(msg):
    print("GuiMessage sent: ", msg)
    pass  # TODO: implement sending


# Get user id from commandline - only for testing purpose
if len(sys.argv) > 1:
    user_id = int(sys.argv[1])
else:
    user_id = 1


window = ChatWindow(user_id)
window.subscribe_message_send(send_message)

window.run()
window.close()
