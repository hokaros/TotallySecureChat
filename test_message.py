import unittest
from message import Message
from copy import deepcopy


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


if __name__ == '__main__':
    unittest.main()
