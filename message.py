from enum import Enum


SENDER_ID_BYTES = 4
MESSAGE_TYPE_BYTES = 1


class MessageType(Enum):
    
    # Session key transfer:
    # -> body can be decrypted using our private key
    SESSION_KEY = 0
    
    # Text self:
    # -> body can be decrypted using a valid session key
    TEXT_MESSAGE = 1


# Low-level self representation
class Message:
    def __init__(self, sender_id: int, type: MessageType, body: bytearray):
        self.sender_id = sender_id
        self.type = type
        self.body = body

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
