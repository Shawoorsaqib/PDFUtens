import io
import os
import unittest
from pypdf import PdfWriter

from app import app
import config


class TestToolsPageAndExtraRoutes(unittest.TestCase):

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

    def test_tools_catalog_page_render(self):
        response = self.client.get("/tools")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"All PDF Tools", response.data)

    def test_compress_pdf_upload_and_download(self):
        pdf_buf = self._generate_dummy_pdf_bytes()
        data = {
            "file": (pdf_buf, "sample_to_compress.pdf")
        }
        response = self.client.post(
            "/compress-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("download_url", json_data)

        # Download compressed file
        download_response = self.client.get(json_data["download_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.mimetype, "application/pdf")

    def test_rotate_pdf_upload_and_download(self):
        pdf_buf = self._generate_dummy_pdf_bytes()
        data = {
            "file": (pdf_buf, "sample_to_rotate.pdf"),
            "angle": "90"
        }
        response = self.client.post(
            "/rotate-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("download_url", json_data)

        # Download rotated file
        download_response = self.client.get(json_data["download_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.mimetype, "application/pdf")


if __name__ == "__main__":
    unittest.main()
