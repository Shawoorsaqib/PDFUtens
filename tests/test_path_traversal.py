import os
import unittest
from app import app
from utils.validators import safe_join_path
from utils.cleanup import delete_file_pair, _safe_remove_file


class TestPathTraversalSecurity(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.output_folder = self.app.config.get("OUTPUT_FOLDER", "outputs")
        self.upload_folder = self.app.config.get("UPLOAD_FOLDER", "uploads")

    def test_safe_join_path_valid_filename(self):
        """Valid filenames inside output folder should pass safe_join_path."""
        valid_filename = "test_document.pdf"
        result = safe_join_path(self.output_folder, valid_filename)
        expected = os.path.realpath(os.path.join(self.output_folder, valid_filename))
        self.assertEqual(result, expected)

    def test_safe_join_path_traversal_payloads(self):
        """Path traversal payloads must raise ValueError."""
        traversal_payloads = [
            "../config.py",
            "..\\config.py",
            "../../app.py",
            "..\\..\\app.py",
            "....//....//config.py",
            "/etc/passwd",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "..%2f..%2fconfig.py"
        ]

        for payload in traversal_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    safe_join_path(self.output_folder, payload)

    def test_download_routes_path_traversal(self):
        """All tool download endpoints must block path traversal payloads with 400 or 404."""
        download_endpoints = [
            "/merge-pdf/download/..%2f..%2fconfig.py",
            "/merge-pdf/download/../config.py",
            "/compress-pdf/download/../config.py",
            "/image-to-pdf/download/../config.py",
            "/pdf-to-word/download/../config.py",
            "/protect-pdf/download/../config.py",
            "/remove-watermark/download/../config.py",
            "/rotate-pdf/download/../config.py",
            "/split-pdf/download/../config.py",
            "/unlock-pdf/download/../config.py",
            "/watermark-pdf/download/../config.py",
            "/word-to-pdf/download/../config.py",
            "/delete-pages/download/../config.py",
            "/extract-pages/download/../config.py",
            "/reorder-pages/download/../config.py",
            "/add-page-numbers/download/../config.py"
        ]

        for endpoint in download_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertIn(response.status_code, [400, 404])
                self.assertNotIn(b"SECRET_KEY", response.data)
                self.assertNotIn(b"import os", response.data)

    def test_cleanup_deletion_path_traversal_protection(self):
        """delete_file_pair and _safe_remove_file must refuse to delete files outside allowed folders."""
        config_path = os.path.abspath("config.py")
        self.assertTrue(os.path.exists(config_path))

        # Attempt to delete config.py using traversal filename
        delete_file_pair("../config.py")
        delete_file_pair("..\\config.py")
        _safe_remove_file(config_path)

        # Verify config.py is unharmed
        self.assertTrue(os.path.exists(config_path), "config.py was deleted by path traversal payload!")


if __name__ == "__main__":
    unittest.main()
