import unittest
from message import Message
from copy import deepcopy
from Crypto.PublicKey import RSA


class MessageConvertingTestCase(unittest.TestCase):
    def test_convert_deconvert_string_equal(self):
        in_string = "Zażółć gęślą jaźń"

        msg = Message.text_message(0, in_string)
        out_string = msg.stringbody()

        assert out_string == in_string

    def test_convert_deconvert_bytes_equal(self):
        # Arrange
        in_string = "Stół z powyłamywanymi nogami"
        msg = Message.text_message(0, in_string)
        original_body = deepcopy(msg.body)  # Remember the body

        # Act
        b = msg.to_bytes()
        out_msg = Message.from_bytes(b)

        # Assert
        assert out_msg.body == original_body

    def test_multiple_from_bytes(self):
        # Arrange
        in_strings = [
            "Stół z powyłamywanymi nogami",
            "Zażółć gęślą jaźń",
            "Blat"
        ]
        messages = [
            Message.text_message(0, string)
            for string in in_strings
        ]

        # Act
        b_sum = bytearray()
        for msg in messages:
            b_sum.extend(msg.to_bytes())

        out_messages, remainders = Message.multiple_from_bytes(b_sum)
        out_strings = [
            msg.stringbody()
            for msg in out_messages
        ]

        # Assert
        self.assertEqual(len(in_strings), len(out_strings))
        for expected, actual in zip(in_strings, out_strings):
            self.assertEqual(expected, actual)

    def test_rsa_key(self):
        # Arrange
        in_key = RSA.generate(1024).public_key()

        # Act
        key_msg = Message.public_key(0, bytearray(in_key.export_key()))
        out_key = RSA.import_key(key_msg.body)

        # Assert
        self.assertEqual(in_key, out_key)


if __name__ == '__main__':
    unittest.main()
