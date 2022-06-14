from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from message import Message, MessageType
from pki_manager import PkiManager, RsaKey


class EncryptedMessage:
    NUM_SIZE = 4

    def __init__(self, ciphertext: bytes, cipher_mode, block_size: int):
        self.ciphertext = ciphertext
        self.cipher_mode = cipher_mode
        self.block_size = block_size

    def to_bytes(self) -> bytes:
        b = bytearray(
            self.cipher_mode.to_bytes(self.NUM_SIZE, "little")
        )
        b.extend(self.block_size.to_bytes(self.NUM_SIZE, "little"))

        b.extend(self.ciphertext)

        return b

    @classmethod
    def from_bytes(cls, b: bytes):
        byte_cursor = 0

        cipher_mode = int.from_bytes(b[byte_cursor:byte_cursor + cls.NUM_SIZE], "little")
        byte_cursor += cls.NUM_SIZE

        block_size = int.from_bytes(b[byte_cursor:byte_cursor + cls.NUM_SIZE], "little")
        byte_cursor += cls.NUM_SIZE

        ciphertext = b[byte_cursor:]

        return cls(ciphertext, cipher_mode, block_size)

    @classmethod
    def read_mode(cls, b: bytes):
        return int.from_bytes(b[0:cls.NUM_SIZE], "little")


class CbcEncryptedMessage(EncryptedMessage):
    def __init__(self, ciphertext: bytes, cipher_mode, block_size: int, iv: bytes):
        super().__init__(ciphertext, cipher_mode, block_size)
        self.iv = iv

    def to_bytes(self) -> bytes:
        b = bytearray(
            self.cipher_mode.to_bytes(self.NUM_SIZE, "little")
        )
        b.extend(self.block_size.to_bytes(self.NUM_SIZE, "little"))

        b.extend(len(self.iv).to_bytes(self.NUM_SIZE, "little"))
        b.extend(self.iv)

        b.extend(self.ciphertext)

        return b

    @classmethod
    def from_bytes(cls, b: bytes):
        byte_cursor = 0

        cipher_mode = int.from_bytes(b[byte_cursor:byte_cursor + cls.NUM_SIZE], "little")
        byte_cursor += cls.NUM_SIZE

        block_size = int.from_bytes(b[byte_cursor:byte_cursor + cls.NUM_SIZE], "little")
        byte_cursor += cls.NUM_SIZE

        iv_size = int.from_bytes(b[byte_cursor:byte_cursor + cls.NUM_SIZE], "little")
        byte_cursor += cls.NUM_SIZE

        iv = b[byte_cursor:byte_cursor + iv_size]
        byte_cursor += iv_size

        ciphertext = b[byte_cursor:]

        return cls(ciphertext, cipher_mode, block_size, iv)


class EncryptedMessageFactory:
    @staticmethod
    def build(ciphertext: bytes, mode, cipher) -> EncryptedMessage:
        if mode == AES.MODE_CBC:
            return CbcEncryptedMessage(ciphertext, mode, AES.block_size, cipher.iv)
        elif mode == AES.MODE_ECB:
            return EncryptedMessage(ciphertext, mode, AES.block_size)

        raise NotImplementedError(f"Encryption mode {mode} not supported")


class MessageEncryptor:
    SESSION_KEY_SIZE = 16
    IV_SIZE = 16

    def __init__(self, user_id: str = "", password: str = "", session_key=None):
        self.__mode = AES.MODE_ECB

        if session_key is None:
            session_key = get_random_bytes(self.SESSION_KEY_SIZE)
        self.session_key = session_key

        if user_id != "":
            self.__pki = PkiManager(user_id, password)

    @property
    def pki(self) -> PkiManager:
        return self.__pki

    @property
    def my_public_key(self) -> RsaKey:
        return self.__pki.public_key

    def use_ecb(self):
        self.__mode = AES.MODE_ECB

    def use_cbc(self):
        self.__mode = AES.MODE_CBC

    def encrypt_bytes(self, msg: bytes) -> bytes:
        if self.__mode == AES.MODE_CBC:
            iv = get_random_bytes(self.IV_SIZE)
            cipher = AES.new(self.session_key, self.__mode, iv)
        else:
            cipher = AES.new(self.session_key, self.__mode)

        msg = pad(msg, AES.block_size)

        ciphertext = cipher.encrypt(msg)

        return EncryptedMessageFactory.build(ciphertext, self.__mode, cipher).to_bytes()

    def decrypt_bytes(self, msg: bytes) -> bytes:
        mode = EncryptedMessage.read_mode(msg)

        if mode == AES.MODE_CBC:
            encrypted_msg = CbcEncryptedMessage.from_bytes(msg)
            cipher = AES.new(self.session_key, mode, iv=encrypted_msg.iv)
        else:
            encrypted_msg = EncryptedMessage.from_bytes(msg)
            cipher = AES.new(self.session_key, mode)

        plaintext = cipher.decrypt(encrypted_msg.ciphertext)
        try:
            plaintext = unpad(plaintext, encrypted_msg.block_size)
        except ValueError:
            pass
        return plaintext

    def encrypt_with_public(self, msg: bytes, receiver_id: str) -> bytes:
        key = self.__pki.load_public_key(receiver_id)
        return PKCS1_OAEP.new(key).encrypt(msg)

    def decrypt_with_private(self, msg: bytes) -> bytes:
        try:
            return PKCS1_OAEP.new(self.__pki.private_key).decrypt(msg)
        except ValueError:
            return get_random_bytes(self.SESSION_KEY_SIZE)

    def encrypt(self, msg: Message) -> None:
        if msg.type == MessageType.SESSION_KEY:
            msg.body = self.encrypt_with_public(msg.body, msg.receiver_id)
        elif msg.type == MessageType.PUBLIC_KEY\
                or msg.type == MessageType.FILE_NAME_MESSAGE:
            pass  # don't encrypt
        else:
            msg.body = self.encrypt_bytes(msg.body)

    def decrypt(self, msg: Message) -> None:
        if msg.type == MessageType.SESSION_KEY:
            msg.body = self.decrypt_with_private(msg.body)
        elif msg.type == MessageType.PUBLIC_KEY\
                or msg.type == MessageType.FILE_NAME_MESSAGE:
            pass  # not encrypted
        else:
            msg.body = self.decrypt_bytes(msg.body)

    @staticmethod
    def generate_session_key() -> bytes:
        return get_random_bytes(MessageEncryptor.SESSION_KEY_SIZE)
