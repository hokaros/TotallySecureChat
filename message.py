from enum import Enum


SENDER_ID_BYTES = 4
MESSAGE_TYPE_BYTES = 1
FILE_MESSAGE_LEN = 64  # the length of file message segment in bytes


class MessageType(Enum):
    
    # Session key transfer:
    # -> body can be decrypted using our private key
    SESSION_KEY = 0
    
    # Text self:
    # -> body can be decrypted using a valid session key
    TEXT_MESSAGE = 1

    # File message:
    # -> body can be decrypted using a valid session key
    # -> needs to be transferred in parts
    FILE_MESSAGE = 2

    # File name message:
    # -> body is a name of a file
    FILE_NAME_MESSAGE = 3


# Low-level message representation
class Message:
    def __init__(self, sender_id: int, type: MessageType, body: bytearray, receiver_id=None):
        self.sender_id = sender_id
        self.type = type
        self.body = body
        self.receiver_id = receiver_id

    def stringbody(self) -> str:
        """Returns the body as a string"""
        return self.body.decode("utf-8", "strict")

    def to_bytes(self) -> bytearray:
        b = self.sender_id.to_bytes(SENDER_ID_BYTES, "little")
        b = bytearray(b)
        b.extend(self.type.value.to_bytes(MESSAGE_TYPE_BYTES, "little"))
        b.extend(self.body)
        return b

    @staticmethod
    def file_message_len():
        return FILE_MESSAGE_LEN

    @staticmethod
    def from_bytes(bytes: bytes):
        byte_cursor = 0

        msg_sender_id = int.from_bytes(bytes[byte_cursor : byte_cursor + SENDER_ID_BYTES], "little")
        byte_cursor += SENDER_ID_BYTES

        msg_type = MessageType(int.from_bytes(bytes[byte_cursor : byte_cursor + MESSAGE_TYPE_BYTES], "little"))
        byte_cursor += MESSAGE_TYPE_BYTES

        msg_body = bytearray(bytes[byte_cursor:])
        return Message(msg_sender_id, msg_type, msg_body)

    @classmethod
    def text_message(cls, sender_id: int, text: str):
        bytes = bytearray(text, "utf-8")
        return cls(sender_id, MessageType.TEXT_MESSAGE, bytes)

    @classmethod
    def file_message(cls, sender_id: int, body: bytearray):
        return cls(sender_id, MessageType.FILE_MESSAGE, body)

    @classmethod
    def file_name_message(cls, sender_id: int, body: bytearray):
        return cls(sender_id, MessageType.FILE_NAME_MESSAGE, body)

    @classmethod
    def session_key(cls, sender_id, session_key: bytearray, receiver_id):
        return cls(sender_id, MessageType.SESSION_KEY, session_key, receiver_id=receiver_id)
