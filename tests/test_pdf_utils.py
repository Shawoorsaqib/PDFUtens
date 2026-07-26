import os
import unittest
import tempfile
from pypdf import PdfWriter, PdfReader
from utils.pdf_utils import merge_pdfs
import config


class TestPDFUtils(unittest.TestCase):

    def setUp(self):
        # Ensure temp, upload, and output directories exist
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

        # Create two dummy PDF files
        self.temp_pdf_1 = self._create_dummy_pdf("Page 1 content")
        self.temp_pdf_2 = self._create_dummy_pdf("Page 2 content")

    def tearDown(self):
        for path in [self.temp_pdf_1, self.temp_pdf_2]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def _create_dummy_pdf(self, text_content):
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        fd, path = tempfile.mkstemp(suffix=".pdf", dir=config.UPLOAD_FOLDER)
        with os.fdopen(fd, "wb") as f:
            writer.write(f)
        writer.close()
        return path

    def test_merge_pdfs_success(self):
        out_filename, out_path = merge_pdfs([self.temp_pdf_1, self.temp_pdf_2])

        self.assertTrue(os.path.exists(out_path))
        self.assertTrue(out_filename.endswith(".pdf"))

        reader = PdfReader(out_path)
        self.assertEqual(len(reader.pages), 2)
        reader.stream.close()

        if os.path.exists(out_path):
            os.remove(out_path)

    def test_merge_pdfs_custom_name(self):
        out_filename, out_path = merge_pdfs([self.temp_pdf_1, self.temp_pdf_2], output_name="custom_test")
        self.assertEqual(out_filename, "custom_test.pdf")
        self.assertTrue(os.path.exists(out_path))

        if os.path.exists(out_path):
            os.remove(out_path)

    def test_merge_pdfs_less_than_two_files(self):
        with self.assertRaises(ValueError):
            merge_pdfs([self.temp_pdf_1])

        with self.assertRaises(ValueError):
            merge_pdfs([])

    def test_merge_pdfs_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            merge_pdfs([self.temp_pdf_1, "non_existent_file.pdf"])


if __name__ == "__main__":
    unittest.main()
