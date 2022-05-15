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
        encryptor = MessageEncryptor(get_random_bytes(16))

        # Act
        encrypted_msg = encryptor.encrypt(msg)
        out_msg = encryptor.decrypt(encrypted_msg)

        # Assert
        self.assertEqual(msg, out_msg)


if __name__ == '__main__':
    unittest.main()
