import io
import os
import unittest
from pypdf import PdfWriter

from app import app
import config


class TestPdfToWordRoute(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

    def _generate_dummy_pdf_bytes(self):
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        buf = io.BytesIO()
        writer.write(buf)
        buf.seek(0)
        writer.close()
        return buf

    def test_pdf_to_word_page_render(self):
        response = self.client.get("/pdf-to-word")
        self.assertEqual(response.status_code, 200)

    def test_pdf_to_word_upload_no_file(self):
        response = self.client.post(
            "/pdf-to-word/upload",
            data={},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("no file uploaded", json_data["message"].lower())

    def test_pdf_to_word_upload_invalid_extension(self):
        data = {
            "file": (io.BytesIO(b"Hello world text content"), "sample.txt")
        }
        response = self.client.post(
            "/pdf-to-word/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("unsupported file format", json_data["message"].lower())

    def test_pdf_to_word_upload_and_download_success(self):
        pdf_buf = self._generate_dummy_pdf_bytes()
        data = {
            "file": (pdf_buf, "sample_document.pdf")
        }
        response = self.client.post(
            "/pdf-to-word/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("download_url", json_data)
        self.assertIn("filename", json_data)

        # Download the generated .docx file
        download_url = json_data["download_url"]
        download_response = self.client.get(download_url)
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(
            download_response.mimetype,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        self.assertTrue(len(download_response.data) > 0)

        # Verify that the generated file was removed from disk after downloading
        output_filename = json_data["filename"]
        output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
        self.assertFalse(os.path.exists(output_path))

    def test_download_nonexistent_file(self):
        response = self.client.get("/pdf-to-word/download/nonexistent_file.docx")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
