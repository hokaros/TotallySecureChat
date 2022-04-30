from enum import Enum
import json
from copy import deepcopy


class MessageType(Enum):
    
    # Session key transfer:
    # -> body can be decrypted using our private key
    SESSION_KEY = 0
    
    # Text self:
    # -> body can be decrypted using a valid session key
    TEXT_MESSAGE = 1


# Low-level self representation
class Message:
    def __init__(self, type: MessageType, body: bytearray):
        self.type = type
        self.body = body

    def stringbody(self) -> str:
        """Returns the body as a string"""
        return self.body.decode("utf-8", "strict")

    def to_bytes(self) -> bytearray:
        b = bytearray(self.type.value)
        b.extend(self.body)
        return b

    @staticmethod
    def from_bytes(bytes: bytes):
        msg_type = MessageType(bytes[0])
        msg_body = bytearray(bytes[1:])
        return Message(msg_type, msg_body)

    @classmethod
    def text_message(cls, text: str):
        bytes = bytearray(text, "utf-8")
        return cls(MessageType.TEXT_MESSAGE, bytes)


# Responsible for encrypting and decrypting
class MessageEncryptor:
    def __init__(self):
        pass #TODO
