import io
import os
import unittest
from pypdf import PdfWriter

from app import app
import config


class TestMergeRoute(unittest.TestCase):

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


    def test_merge_pdf_page_render(self):
        response = self.client.get("/merge-pdf")
        self.assertEqual(response.status_code, 200)

    def test_merge_pdf_upload_insufficient_files(self):
        data = {
            "file": (io.BytesIO(b"dummy"), "doc1.pdf")
        }
        response = self.client.post(
            "/merge-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("at least two", json_data["message"].lower())

    def test_merge_pdf_upload_and_download_success(self):
        pdf1 = io.BytesIO()
        pdf2 = io.BytesIO()
        
        w1 = PdfWriter()
        w1.add_blank_page(width=600, height=800)
        w1.write(pdf1)
        pdf1.seek(0)

        w2 = PdfWriter()
        w2.add_blank_page(width=600, height=800)
        w2.write(pdf2)
        pdf2.seek(0)

        data = {
            "file": [
                (pdf1, "test1.pdf"),
                (pdf2, "test2.pdf")
            ]
        }

        response = self.client.post(
            "/merge-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("download_url", json_data)
        self.assertIn("filename", json_data)

        download_url = json_data["download_url"]
        download_response = self.client.get(download_url)
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.mimetype, "application/pdf")
        self.assertTrue(len(download_response.data) > 0)

    def test_merge_three_pdfs_success(self):
        pdf_bufs = []
        for _ in range(3):
            buf = io.BytesIO()
            w = PdfWriter()
            w.add_blank_page(width=500, height=500)
            w.write(buf)
            buf.seek(0)
            pdf_bufs.append(buf)

        data = {
            "file": [
                (pdf_bufs[0], "file1.pdf"),
                (pdf_bufs[1], "file2.pdf"),
                (pdf_bufs[2], "file3.pdf")
            ]
        }

        response = self.client.post(
            "/merge-pdf/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("download_url", json_data)

    def test_download_nonexistent_file(self):
        response = self.client.get("/merge-pdf/download/nonexistent_file.pdf")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
