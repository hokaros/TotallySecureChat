from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from message import Message, MessageType


class EncryptedMessage:
    NUM_SIZE = 4

    def __init__(self, ciphertext: bytes, tag: bytes, nonce: bytes):
        self.ciphertext = ciphertext
        self.tag = tag
        self.nonce = nonce

    def to_bytes(self) -> bytes:
        b = bytearray(
            len(self.tag).to_bytes(self.NUM_SIZE, "little")
        )
        b.extend(self.tag)

        b.extend(
            len(self.nonce).to_bytes(self.NUM_SIZE, "little")
        )
        b.extend(self.nonce)

        b.extend(self.ciphertext)

        return b

    @classmethod
    def from_bytes(cls, b: bytes):
        byte_cursor = 0
        tag_size = int.from_bytes(b[byte_cursor:byte_cursor + cls.NUM_SIZE], "little")
        byte_cursor += cls.NUM_SIZE

        tag = b[byte_cursor:byte_cursor + tag_size]
        byte_cursor += tag_size

        nonce_size = int.from_bytes(b[byte_cursor:byte_cursor + cls.NUM_SIZE], "little")
        byte_cursor += cls.NUM_SIZE

        nonce = b[byte_cursor:byte_cursor + nonce_size]
        byte_cursor += nonce_size

        ciphertext = b[byte_cursor:]

        return cls(ciphertext, tag, nonce)


class MessageEncryptor:
    SESSION_KEY_SIZE = 16

    def __init__(self, session_key=None):
        if session_key is None:
            session_key = get_random_bytes(self.SESSION_KEY_SIZE)
        self.session_key = session_key

    def encrypt_bytes(self, msg: bytes) -> bytes:
        # TODO: different ciphering modes
        cipher = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(msg)

        return EncryptedMessage(ciphertext, tag, cipher.nonce).to_bytes()

    def decrypt_bytes(self, msg: bytes) -> bytes:
        encrypted_msg = EncryptedMessage.from_bytes(msg)

        cipher = AES.new(self.session_key, AES.MODE_EAX, nonce=encrypted_msg.nonce)
        plaintext = cipher.decrypt_and_verify(encrypted_msg.ciphertext, encrypted_msg.tag)
        return plaintext

    def encrypt(self, msg: Message) -> None:
        if msg.type == MessageType.SESSION_KEY:
            pass  # TODO: implement encrypting with public key
        else:
            msg.body = self.encrypt_bytes(msg.body)

    def decrypt(self, msg: Message) -> None:
        if msg.type == MessageType.SESSION_KEY:
            pass  # TODO: implement decrypting with private key
        else:
            msg.body = self.decrypt_bytes(msg.body)

    @staticmethod
    def generate_session_key() -> bytes:
        return get_random_bytes(MessageEncryptor.SESSION_KEY_SIZE)
