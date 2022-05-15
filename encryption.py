from Crypto.Cipher import AES


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
    def __init__(self, session_key):
        self.session_key = session_key
        pass

    def encrypt(self, msg: bytes) -> bytes:
        cipher = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(msg)

        return EncryptedMessage(ciphertext, tag, cipher.nonce).to_bytes()

    def decrypt(self, msg: bytes) -> bytes:
        encrypted_msg = EncryptedMessage.from_bytes(msg)

        cipher = AES.new(self.session_key, AES.MODE_EAX, nonce=encrypted_msg.nonce)
        plaintext = cipher.decrypt_and_verify(encrypted_msg.ciphertext, encrypted_msg.tag)
        return plaintext
