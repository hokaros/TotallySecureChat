from gui_messages import *
from typing import Callable
import PySimpleGUI as sg


class ChatWindow:
    def __init__(self, user_id):
        self.__on_message_send = []

        self.__window = self.__create_window()

        self.message_displayer = MessageDisplayer(self.__window, user_id)
        self.message_displayer.display_messages()

    def subscribe_message_send(self, callback: Callable[[str], None]):
        self.__on_message_send.append(callback)

    def receive_message(self, msg, sender_id):
        self.message_displayer.receive_message(msg, sender_id)

    def run(self):
        while True:
            event, values = self.__window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == 'Send':
                msg = values[0]
                if len(msg) > 0:
                    self.__invoke_message_send(msg)
                    self.message_displayer.on_send(msg)

    def close(self):
        self.__window.close()

    @staticmethod
    def __create_window() -> sg.Window:
        messages = [[sg.Text("", key=('_MSG_' + str(i)), background_color="#00111a", pad=((10, 10), (4, 4)),
                             relief="flat", border_width=10, expand_y=True, justification='right')] for i in
                    range(MESSAGES_ON_SCREEN + 1)]

        sg.theme('DarkBlue')

        layout = [
            [sg.Column(messages, size=(400, 300), background_color="#00111a", vertical_alignment="bottom")],
            [sg.InputText(do_not_clear=False, size=20), sg.Button('Send', bind_return_key=True, pad=((0, 20), (20, 20)))
                , sg.FileBrowse('Send File')],
            [sg.Text(text="DżejEs&EjEl Software")]
        ]

        window = sg.Window('Totally Secure Chat', layout, font = ('Segoe UI Light', 16))
        window.finalize()
        return window

    def __invoke_message_send(self, msg):
        for callback in self.__on_message_send:
            callback(msg)
