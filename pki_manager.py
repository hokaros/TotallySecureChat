import os

from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Hash import SHA256
from os.path import exists
from threading import Lock
from filewriter import UserDirectory


_PUBLIC_DIRECTORY = "public"
_PRIVATE_DIRECTORY = "private"

KEY_LENGTH = 2048


class PkiManager:
    class_lock = Lock()

    def __init__(self, user_id: str, password: str):
        self.__user_id = user_id
        self.__private_key = None
        self.__public_key = None
        self.__password = password

        self.validate_directories()
        if self.try_load_private_key():
            self.__public_key = self.load_public_key(self.__user_id)
        else:
            self.generate_and_save_keys()

    @property
    def private_key(self):
        return self.__private_key

    @property
    def public_key(self):
        return self.__public_key

    def validate_directories(self):
        if not exists(self.public_directory()):
            os.makedirs(self.public_directory())

        if not exists(self.private_directory()):
            os.makedirs(self.private_directory())

    def generate_and_save_keys(self):
        self.class_lock.acquire()

        password_hash = self.__password_hash()

        key = RSA.generate(KEY_LENGTH)
        private_encrypted = key.export_key(passphrase=password_hash)
        public_encrypted = key.public_key().export_key(passphrase=password_hash)

        # Save to files
        private_file = PkiManager.private_key_filepath(self.__user_id)
        with open(private_file, "wb") as f:
            f.write(private_encrypted)
            self.__private_key = key

        public_file = PkiManager.public_key_filepath(self.__user_id)
        with open(public_file, "wb") as f:
            f.write(public_encrypted)
            self.__public_key = key.public_key()

        self.class_lock.release()

    def save_public_key(self, user_id: str, key: RsaKey):
        encrypted_key = key.export_key(passphrase=self.__password_hash())

        with open(PkiManager.public_key_filepath(user_id), "wb") as f:
            f.write(encrypted_key)

    def try_load_private_key(self) -> bool:
        self.class_lock.acquire()

        key_file = PkiManager.private_key_filepath(self.__user_id)
        if not exists(key_file):
            self.class_lock.release()
            return False

        with open(key_file, "rb") as f:
            try:
                key = RSA.import_key(f.read(), passphrase=self.__password_hash())
            except ValueError:
                key = RSA.generate(KEY_LENGTH)  # Random key
            self.__private_key = key

            self.class_lock.release()
            return True

    def load_public_key(self, user_id: str) -> RsaKey | None:
        key_file = PkiManager.public_key_filepath(user_id)
        if not exists(key_file):
            return None

        with open(key_file, "rb") as f:
            return RSA.import_key(f.read(), passphrase=self.__password_hash())

    def __password_hash(self) -> str:
        return SHA256.new(
                self.__password.encode("utf-8", "strict")
            ).hexdigest()

    @staticmethod
    def public_key_filepath(user_id: str) -> str:
        filename = f"public_{user_id}.pem"
        directory = PkiManager.public_directory()
        return os.path.join(directory, filename)

    @staticmethod
    def public_directory() -> str:
        return os.path.join(UserDirectory.main.directory, _PUBLIC_DIRECTORY)

    @staticmethod
    def private_key_filepath(user_id: str) -> str:
        filename = f"private_{user_id}.pem"
        directory = PkiManager.private_directory()
        return os.path.join(directory, filename)

    @staticmethod
    def private_directory() -> str:
        return os.path.join(UserDirectory.main.directory, _PRIVATE_DIRECTORY)
