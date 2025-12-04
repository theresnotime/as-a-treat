import unittest
import os
import json
import time
from unittest.mock import MagicMock, patch
import archive
import config

class TestArchive(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_archive.json"
        # Patch config to use test file
        self.original_path = getattr(config, "ARCHIVE_FILE_PATH", "archive.json")
        config.ARCHIVE_FILE_PATH = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        config.ARCHIVE_FILE_PATH = self.original_path
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_save(self):
        data = {"statuses": [{"id": 1}], "meta": {"last_archived": 123}}
        archive.save_archive(data)
        loaded = archive.load_existing_archive()
        self.assertEqual(loaded, data)

    def test_archive_status(self):
        data = {"statuses": [], "meta": {"last_archived": 0}}
        status = {
            "id": 101,
            "created_at": MagicMock(timestamp=lambda: 1000),
            "content": "test",
            "favourites_count": 5,
            "reblogs_count": 2,
            "replies_count": 1
        }
        archive.archive_status(status, data)
        self.assertEqual(len(data["statuses"]), 1)
        self.assertEqual(data["statuses"][0]["id"], 101)
        self.assertEqual(data["statuses"][0]["likes"], 5)
        
        # Update existing
        status["favourites_count"] = 10
        archive.archive_status(status, data)
        self.assertEqual(len(data["statuses"]), 1)
        self.assertEqual(data["statuses"][0]["likes"], 10)

    @patch("archive.Mastodon")
    def test_run_periodic_archive(self, mock_mastodon):
        # Setup mock
        mock_instance = MagicMock()
        mock_mastodon.return_value = mock_instance
        mock_instance.account_verify_credentials.return_value = {"id": 123}
        mock_instance.account_statuses.return_value = []
        
        # Force archive needed
        config.ARCHIVE_INTERVAL_SECONDS = 10
        data = {"statuses": [], "meta": {"last_archived": time.time() - 100}}
        archive.save_archive(data)
        
        archive.run_periodic_archive(dry_run=False)
        
        # Check if API was called
        mock_instance.account_statuses.assert_called()
        
        # Check if timestamp updated
        loaded = archive.load_existing_archive()
        self.assertGreater(loaded["meta"]["last_archived"], data["meta"]["last_archived"])

if __name__ == "__main__":
    unittest.main()
