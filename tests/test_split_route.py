import io
import json
import os
import unittest
from pypdf import PdfWriter, PdfReader

from app import app
import config
from utils.pdf_utils import split_pdf


class TestSplitRoute(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

    def _create_multi_page_pdf_bytes(self, num_pages=3):
        writer = PdfWriter()
        for i in range(num_pages):
            writer.add_blank_page(width=600, height=800)
        buf = io.BytesIO()
        writer.write(buf)
        buf.seek(0)
        writer.close()
        return buf

    def test_split_pdf_page_render(self):
        response = self.client.get("/split-pdf")
        self.assertEqual(response.status_code, 200)

    def test_split_pdf_upload_no_file(self):
        response = self.client.post("/split-pdf/upload", data={}, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])

    def test_split_pdf_upload_all_pages_success(self):
        pdf_bytes = self._create_multi_page_pdf_bytes(num_pages=3)
        data = {
            "file": (pdf_bytes, "sample_3pages.pdf"),
            "split_mode": "all"
        }
        response = self.client.post(
            "/split-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("download_url", json_data)
        self.assertTrue(json_data["filename"].endswith(".zip"))

        # Verify downloading the zip file
        download_response = self.client.get(json_data["download_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.mimetype, "application/zip")
        self.assertTrue(len(download_response.data) > 0)

    def test_split_pdf_upload_custom_range_success(self):
        pdf_bytes = self._create_multi_page_pdf_bytes(num_pages=5)
        ranges = json.dumps([{"from": 2, "to": 4}])
        data = {
            "file": (pdf_bytes, "sample_5pages.pdf"),
            "split_mode": "range",
            "ranges": ranges
        }
        response = self.client.post(
            "/split-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("download_url", json_data)
        self.assertTrue(json_data["filename"].endswith(".pdf"))

        # Verify downloading the single extracted pdf file
        download_response = self.client.get(json_data["download_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.mimetype, "application/pdf")
        
        # Verify page count of generated single PDF
        extracted_reader = PdfReader(io.BytesIO(download_response.data))
        self.assertEqual(len(extracted_reader.pages), 3)

    def test_split_pdf_upload_invalid_range_out_of_bounds(self):
        pdf_bytes = self._create_multi_page_pdf_bytes(num_pages=2)
        ranges = json.dumps([{"from": 1, "to": 10}])
        data = {
            "file": (pdf_bytes, "sample_2pages.pdf"),
            "split_mode": "range",
            "ranges": ranges
        }
        response = self.client.post(
            "/split-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("out of bounds", json_data["message"].lower())


if __name__ == "__main__":
    unittest.main()
