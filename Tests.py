"""
tests for db (partial tests)
by Bar Assulin ~ 27/5/25
"""

import unittest
from unittest.mock import MagicMock, patch
from database import Database  # replace with actual filename


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database("localhost", "root", "Zaq1@wsx", "localhost")

    def test_add_to_db_success(self):
        # Mock cursor and commit
        mock_cursor = MagicMock()
        self.db.commit = MagicMock()

        result = self.db.add_to_db(mock_cursor, "clients", "'1','John','token123'")
        mock_cursor.execute.assert_called_with("INSERT INTO clients VALUES ('1','John','token123')")
        self.db.commit.assert_called_once()
        self.assertTrue(result)

    def test_add_to_db_failure(self):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        self.db.commit = MagicMock()

        result = self.db.add_to_db(mock_cursor, "clients", "'1','John','token123'")
        self.assertFalse(result)
        self.db.commit.assert_not_called()
    """
    def test_read_from_db(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("Alice", 30), ("Bob", 25)]

        result = self.db.read_from_db(mock_cursor, "users", "*")
        mock_cursor.execute.assert_called_with("SELECT * FROM users")
        self.assertEqual(result, [("Alice", 30), ("Bob", 25)])
    """


if __name__ == '__main__':
    unittest.main()
