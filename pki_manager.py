import os

from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Hash import SHA256
from os.path import exists
from threading import Lock


PUBLIC_DIRECTORY = "public"
PRIVATE_DIRECTORY = "private"

KEY_LENGTH = 2048


class PkiManager:
    class_lock = Lock()

    def __init__(self, user_id: str, password: str):
        self.__user_id = user_id
        self.__private_key = None
        self.__password = password

        self.validate_directories()
        if not self.try_load_private_key():
            self.generate_and_save_keys()

    @property
    def private_key(self):
        return self.__private_key

    def validate_directories(self):
        if not exists(PUBLIC_DIRECTORY):
            os.makedirs(PUBLIC_DIRECTORY)

        if not exists(PRIVATE_DIRECTORY):
            os.makedirs(PRIVATE_DIRECTORY)

    def generate_and_save_keys(self):
        self.class_lock.acquire()

        password_hash = SHA256.new(
            self.__password.encode("utf-8", "strict")
        ).hexdigest()

        key = RSA.generate(KEY_LENGTH)
        private_encrypted = key.export_key(passphrase=password_hash)

        # Save to files
        private_file = PkiManager.private_key_filepath(self.__user_id)
        with open(private_file, "wb") as f:
            f.write(private_encrypted)
            self.__private_key = key

        public_file = PkiManager.public_key_filepath(self.__user_id)
        with open(public_file, "wb") as f:
            f.write(key.public_key().export_key())

        self.class_lock.release()

    def try_load_private_key(self) -> bool:
        self.class_lock.acquire()

        key_file = PkiManager.private_key_filepath(self.__user_id)
        if not exists(key_file):
            self.class_lock.release()
            return False

        with open(key_file, "rb") as f:
            password_hash = SHA256.new(
                self.__password.encode("utf-8", "strict")
            ).hexdigest()

            try:
                key = RSA.import_key(f.read(), passphrase=password_hash)
            except ValueError:
                key = RSA.generate(KEY_LENGTH)  # Random key
            self.__private_key = key

            self.class_lock.release()
            return True

    @staticmethod
    def load_public_key(user_id: str) -> RsaKey | None:
        key_file = PkiManager.public_key_filepath(user_id)
        if not exists(key_file):
            return None

        with open(key_file, "rb") as f:
            return RSA.import_key(f.read())

    @staticmethod
    def public_key_filepath(user_id: str) -> str:
        return f"{PUBLIC_DIRECTORY}/public_{user_id}.pem"

    @staticmethod
    def private_key_filepath(user_id: str) -> str:
        return f"{PRIVATE_DIRECTORY}/private_{user_id}.pem"
