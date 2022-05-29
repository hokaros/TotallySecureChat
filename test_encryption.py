import os.path
import unittest
from encryption import *
from Crypto.Random import get_random_bytes


class EncryptionTestCase(unittest.TestCase):
    def test_bytes_convert_deconvert_equal(self):
        # Arrange
        ciphertext = b'\x00\xff\x00\xff'
        tag = b'\xff\xff\xff\xff\xff\xff'
        nonce = b'\xaa\xaa\xaa'
        msg = EncryptedMessage(ciphertext, tag, nonce)

        # Act
        b = msg.to_bytes()
        out_msg = EncryptedMessage.from_bytes(b)

        # Assert
        self.assertEqual(msg.ciphertext, out_msg.ciphertext)
        self.assertEqual(msg.tag, out_msg.tag)
        self.assertEqual(msg.nonce, out_msg.nonce)

    def test_encrypt_decrypt_equal(self):
        # Arrange
        msg = bytearray("Stół z powyłamywanymi nogami", "utf-8")
        encryptor = MessageEncryptor("", "", session_key=get_random_bytes(16))

        # Act
        encrypted_msg = encryptor.encrypt_bytes(msg)
        out_msg = encryptor.decrypt_bytes(encrypted_msg)

        # Assert
        self.assertEqual(msg, out_msg)

    def test_encrypt_decrypt_wrong_key(self):
        # Arrange
        msg = bytearray("Stół z powyłamywanymi nogami", "utf-8")
        session_key = get_random_bytes(16)

        wrong_session_key = bytearray(session_key)
        wrong_session_key[0] = 1 ^ wrong_session_key[0]

        encryptor = MessageEncryptor("", "", session_key=session_key)
        wrong_encryptor = MessageEncryptor("", "", session_key=wrong_session_key)

        # Act
        encrypted_msg = encryptor.encrypt_bytes(msg)
        out_msg = wrong_encryptor.decrypt_bytes(encrypted_msg)

        # Assert
        self.assertNotEqual(msg, out_msg)

    def test_asymmetric_encrypt_decrypt_equal(self):
        # Arrange
        receiver_id = "8080"
        if os.path.exists(PkiManager.private_key_filepath(receiver_id)):
            os.remove(PkiManager.private_key_filepath(receiver_id))

        in_bytes = get_random_bytes(16)
        encryptor = MessageEncryptor(receiver_id, receiver_id)

        # Act
        encrypted_msg = encryptor.encrypt_with_public(in_bytes, receiver_id)
        out_msg = encryptor.decrypt_with_private(encrypted_msg)

        # Assert
        self.assertNotEqual(in_bytes, encrypted_msg)
        self.assertEqual(in_bytes, out_msg)

        # Clean up
        os.remove(PkiManager.private_key_filepath(receiver_id))

    def test_asymmetric_wrong_password(self):
        # Arrange
        receiver_id = "8080"
        if os.path.exists(PkiManager.private_key_filepath(receiver_id)):
            os.remove(PkiManager.private_key_filepath(receiver_id))

        in_bytes = get_random_bytes(16)

        password = "secret-password"
        encryptor = MessageEncryptor(receiver_id, password)
        wrong_encryptor = MessageEncryptor(receiver_id, password + "nanananana")

        # Act
        encrypted_msg = encryptor.encrypt_with_public(in_bytes, receiver_id)
        wrong_password_msg = wrong_encryptor.decrypt_with_private(encrypted_msg)

        # Assert
        self.assertNotEqual(in_bytes, wrong_password_msg)

        # Clean up
        os.remove(PkiManager.private_key_filepath(receiver_id))


if __name__ == '__main__':
    unittest.main()
