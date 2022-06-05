from typing import List, Tuple


MESSAGES_ON_SCREEN = 5


class GuiMessage:
    def __init__(self, client_id, _author, _text) -> None:
        self.__client_id = client_id
        self.author = _author
        self.text = _text

    def getColor(self):
        if self.author == self.__client_id:
            return "#006697"  # For our own messages
        else:
            return "#00324d"

    def getLeftPad(self):
        if self.author == self.__client_id:
            return 5  # For our own messages
        else:
            return 20


class MessageDisplayer:
    def __init__(self, window, user_id):
        self.window = window
        self.user_id = user_id

        self.message_history: List[GuiMessage] = []

        self.current_top_message = len(self.message_history) - MESSAGES_ON_SCREEN
        if self.current_top_message < 0:
            self.current_top_message = 0

    def on_send(self, msg):
        self.receive_message(msg, self.user_id)

    def on_file_send(self, filepath):
        self.receive_file(filepath, self.user_id)

    def receive_message(self, msg, sender_id):
        self.message_history.append(GuiMessage(self.user_id, sender_id, msg))

        if len(self.message_history) > MESSAGES_ON_SCREEN:
            self.current_top_message += 1

        self.display_messages()

    def receive_file(self, filename, sender_id):
        self.message_history.append(GuiMessage(self.user_id, sender_id, filename))

        if len(self.message_history) > MESSAGES_ON_SCREEN:
            self.current_top_message += 1

        self.display_messages()

    def display_messages(self):
        for i in range(MESSAGES_ON_SCREEN + 1):
            if self.current_top_message + i < len(self.message_history):
                current_message = self.message_history[self.current_top_message + i]
                self.window[('_MSG_' + str(i))].Update(current_message.text, background_color=current_message.getColor())
            else:
                self.window[('_MSG_' + str(i))].Update("", background_color="#00111a")
