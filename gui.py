import PySimpleGUI as sg
import sys

messages_on_screen = 5

class message:
    def __init__(self, _author, _text) -> None:
        self.author = _author
        self.text = _text

    def getColor(self):
        if self.author == 1:
            return "#006697"
        else: return "#00324d"

    def getLeftPad(self):
        if self.author == 1:
            return 5
        else: return 20

# only for testing purpose
if len(sys.argv) > 1:
    user_id = int(sys.argv[1])
else: user_id = 1

message_history = [message(1, "No siema"), message(2, "Joł, co tam?"), message(1, "JHD"), message(2, "JHD")]
# TODO: integrate with real message sending

current_top_message = len(message_history)-messages_on_screen
if current_top_message < 0: current_top_message = 0


messages = [[sg.Text("", key=('_MSG_'+str(i)), background_color = "#00111a", pad=((10, 10), (4, 4)), relief="flat", border_width=10, expand_y = True, justification='right')] for i in range(messages_on_screen+1)]

sg.theme('DarkBlue')

def display_messages(starting_index):
    for i in range(messages_on_screen+1):
        if starting_index + i < len(message_history):
            current_message = message_history[starting_index + i]
            window[('_MSG_' + str(i))].Update(current_message.text, background_color = current_message.getColor())
        else:
            window[('_MSG_' + str(i))].Update("", background_color = "#00111a")

layout = [
    [sg.Column(messages, size=(400,300), background_color="#00111a", vertical_alignment="bottom")],
    [sg.InputText(do_not_clear=False, size=20), sg.Button('Send', bind_return_key=True, pad=((0, 20),(20, 20))),sg.FileBrowse('Send File')],
    [sg.Text(text="DżejEs&EjEl Software")] 
    ]

window = sg.Window('Wyjątkowo Bezpieczny Komunikator', layout, font = ('Segoe UI Light', 16))
window.finalize()
display_messages(current_top_message)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Send':
        if len(values[0]) > 0: 
            message_history.append(message(user_id, values[0]))
            if(len(message_history)>messages_on_screen):
                current_top_message += 1
            display_messages(current_top_message)
        
    
window.close()