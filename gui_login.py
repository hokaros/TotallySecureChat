from typing import Callable

import PySimpleGUI as sg


class LoginWindow:
    def __init__(self):
        self.__on_confirm = []
        self.__window = self.__create_window()

    def subscribe_confirm(self, callback: Callable[[dict], None]):
        self.__on_confirm.append(callback)

    @staticmethod
    def __create_window() -> sg.Window:
        sg.theme('DarkBlue')
        layout = [[sg.Text('Your port:'), sg.InputText(key='_PORT_', size=20)],
                  [sg.Text('Receiver\'s port:'), sg.InputText(key='_RECEIVER_PORT_', size=20)],
                  [sg.Text('Password:'), sg.InputText(key='_PASSWORD_', size=20, password_char='*')],
                  [sg.Radio('ECB encryption', "ENC", default=False, key="ecb"),
                   sg.Radio('CBC encryption', "ENC", default=True, key="cbc")],
                  [sg.Button('Confirm', bind_return_key=True, pad=((0, 20), (20, 20))),
                   sg.Button('Cancel', bind_return_key=True, pad=((0, 20), (20, 20)))]]

        return sg.Window('Totally Secure Chat', layout)

    def run(self):
        while True:
            event, values = self.__window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel':
                break
            elif event == 'Confirm':
                self.__invoke_confirm(values)
                break

    def close(self):
        self.__window.close()

    def __invoke_confirm(self, values):
        for callback in self.__on_confirm:
            callback(values)
