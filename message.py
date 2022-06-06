from enum import Enum
from typing import List


SENDER_ID_BYTES = 4
MESSAGE_TYPE_BYTES = 1
MESSAGE_LENGTH_BYTES = 4
FILE_SEGMENTS_COUNT_BYTES = 4
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
    def __init__(self, sender_id: int, type: MessageType, body: bytearray, receiver_id=None, segments_count=1):
        self.sender_id = sender_id
        self.type = type
        self.body = body
        self.receiver_id = receiver_id
        self.segments_count = segments_count

    def stringbody(self) -> str:
        """Returns the body as a string"""
        return self.body.decode("utf-8", "ignore")

    def to_bytes(self) -> bytearray:
        b = self.sender_id.to_bytes(SENDER_ID_BYTES, "little")
        b = bytearray(b)
        b.extend(self.type.value.to_bytes(MESSAGE_TYPE_BYTES, "little"))
        b.extend(self.segments_count.to_bytes(FILE_SEGMENTS_COUNT_BYTES, "little"))
        b.extend(self.bytes_size.to_bytes(MESSAGE_LENGTH_BYTES, "little"))
        print("Length: ", self.bytes_size)
        b.extend(self.body)
        return b

    @property
    def bytes_size(self) -> int:
        return SENDER_ID_BYTES + MESSAGE_TYPE_BYTES + MESSAGE_LENGTH_BYTES + FILE_SEGMENTS_COUNT_BYTES + len(self.body)

    @staticmethod
    def file_message_len():
        return FILE_MESSAGE_LEN

    @staticmethod
    def from_bytes(bytes: bytes):
        print("decoding message")
        byte_cursor = 0

        msg_sender_id = int.from_bytes(bytes[byte_cursor: byte_cursor + SENDER_ID_BYTES], "little")
        byte_cursor += SENDER_ID_BYTES
        print(f"sender id: {msg_sender_id}")
        msg_type = MessageType(int.from_bytes(bytes[byte_cursor: byte_cursor + MESSAGE_TYPE_BYTES], "little"))
        byte_cursor += MESSAGE_TYPE_BYTES
        print(f"msg_type: {msg_type}")
        segments_count = int.from_bytes(bytes[byte_cursor: byte_cursor + FILE_SEGMENTS_COUNT_BYTES], "little")
        byte_cursor += FILE_SEGMENTS_COUNT_BYTES
        print(f"segments_count:{segments_count}")
        # no need to read message length, because we consume all the bytes
        byte_cursor += MESSAGE_LENGTH_BYTES

        msg_body = bytearray(bytes[byte_cursor:])
        print(f"message body:{msg_body}")
        return Message(msg_sender_id, msg_type, msg_body, segments_count=segments_count)

    @staticmethod
    def multiple_from_bytes(bytes: bytes | bytearray):
        """Consumes maximum count of messages. Returns them and the unconsumed bytes"""
        messages = []

        while Message.can_read_length(bytes):
            fst_msg_size = Message.read_first_message_length(bytes)
            if len(bytes) < fst_msg_size:
                break

            # Enough bytes to read a message
            fst_message_bytes = bytes[0:fst_msg_size]
            messages.append(Message.from_bytes(fst_message_bytes))

            bytes = bytes[fst_msg_size:]

        return messages, bytes

    @staticmethod
    def read_first_message_length(bytes: bytes) -> int:
        start_index = SENDER_ID_BYTES + MESSAGE_TYPE_BYTES + FILE_SEGMENTS_COUNT_BYTES
        length_bytes = bytes[start_index : start_index + MESSAGE_LENGTH_BYTES]
        return int.from_bytes(length_bytes, "little")

    @staticmethod
    def can_read_length(bytes) -> bool:
        """Tells if the bytes are long enough to contain info about message length"""
        if len(bytes) >= SENDER_ID_BYTES + MESSAGE_TYPE_BYTES + FILE_SEGMENTS_COUNT_BYTES + MESSAGE_LENGTH_BYTES:
            return True
        return False

    @classmethod
    def text_message(cls, sender_id: int, text: str):
        bytes = bytearray(text, "utf-8")
        return cls(sender_id, MessageType.TEXT_MESSAGE, bytes)

    @classmethod
    def file_message(cls, sender_id: int, body: bytearray):
        return cls(sender_id, MessageType.FILE_MESSAGE, body)

    @classmethod
    def file_name_message(cls, sender_id: int, body: bytearray, segments_count: int):
        return cls(sender_id, MessageType.FILE_NAME_MESSAGE, body, segments_count=segments_count)

    @classmethod
    def session_key(cls, sender_id, session_key: bytearray, receiver_id):
        return cls(sender_id, MessageType.SESSION_KEY, session_key, receiver_id=receiver_id)
