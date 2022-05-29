import unittest
import os
from pki_manager import PkiManager


class PkiManagerTestCase(unittest.TestCase):
    def test_get_private_key_wrong_password(self):
        # Arrange
        user_id = "101"
        password = "secret-password"
        generating_manager = PkiManager(user_id, password)
        wrong_password_manager = PkiManager(user_id, password + "nonono")
        correct_password_manager = PkiManager(user_id, password)

        # Act
        generating_manager.generate_and_save_keys()
        wrong_password_manager.try_load_private_key()
        correct_password_manager.try_load_private_key()

        # Assert
        self.assertNotEqual(
            generating_manager.private_key,
            wrong_password_manager.private_key)

        self.assertEqual(
            generating_manager.private_key,
            correct_password_manager.private_key)

        # Clean up
        os.remove(PkiManager.private_key_filepath(user_id))


if __name__ == '__main__':
    unittest.main()
