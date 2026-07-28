import os
import io
import unittest
from app import app
from pypdf import PdfWriter, PdfReader


class TestSecurityRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Create a sample PDF buffer
        w = PdfWriter()
        w.add_blank_page(612, 792)
        pdf_bytes = io.BytesIO()
        w.write(pdf_bytes)
        self.sample_pdf = pdf_bytes.getvalue()

    def tearDown(self):
        self.app_context.pop()

    def test_protect_pdf_route_render(self):
        response = self.client.get("/protect-pdf")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Protect PDF", response.data)

    def test_unlock_pdf_route_render(self):
        response = self.client.get("/unlock-pdf")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unlock PDF", response.data)

    def test_watermark_pdf_route_render(self):
        response = self.client.get("/watermark-pdf")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Watermark PDF", response.data)

    def test_remove_watermark_route_render(self):
        response = self.client.get("/remove-watermark")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Remove Watermark", response.data)

    def test_protect_pdf_upload_and_download(self):
        data = {
            "file": (io.BytesIO(self.sample_pdf), "test.pdf"),
            "password": "secret_password"
        }
        response = self.client.post(
            "/protect-pdf/upload",
            content_type="multipart/form-data",
            data=data
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data.get("success"))
        self.assertIn("download_url", json_data)

        # Download encrypted file
        download_res = self.client.get(json_data["download_url"])
        self.assertEqual(download_res.status_code, 200)
        self.assertEqual(download_res.mimetype, "application/pdf")

        # Verify encryption
        reader = PdfReader(io.BytesIO(download_res.data))
        self.assertTrue(reader.is_encrypted)
        self.assertNotEqual(reader.decrypt("secret_password"), 0)

    def test_unlock_pdf_upload_and_download(self):
        # First protect a PDF
        w = PdfWriter()
        w.add_blank_page(612, 792)
        w.encrypt("my_pass")
        enc_buf = io.BytesIO()
        w.write(enc_buf)

        data = {
            "file": (io.BytesIO(enc_buf.getvalue()), "encrypted.pdf"),
            "password": "my_pass"
        }
        response = self.client.post(
            "/unlock-pdf/upload",
            content_type="multipart/form-data",
            data=data
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data.get("success"))

        # Download unlocked file
        download_res = self.client.get(json_data["download_url"])
        self.assertEqual(download_res.status_code, 200)

        # Verify decryption
        reader = PdfReader(io.BytesIO(download_res.data))
        self.assertFalse(reader.is_encrypted)

    def test_watermark_pdf_upload_and_download(self):
        data = {
            "file": (io.BytesIO(self.sample_pdf), "document.pdf"),
            "text": "CONFIDENTIAL",
            "opacity": "0.3",
            "rotation": "45"
        }
        response = self.client.post(
            "/watermark-pdf/upload",
            content_type="multipart/form-data",
            data=data
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data.get("success"))

        download_res = self.client.get(json_data["download_url"])
        self.assertEqual(download_res.status_code, 200)
        self.assertEqual(download_res.mimetype, "application/pdf")

    def test_remove_watermark_upload_and_download(self):
        data = {
            "file": (io.BytesIO(self.sample_pdf), "watermarked.pdf"),
            "text": "CONFIDENTIAL"
        }
        response = self.client.post(
            "/remove-watermark/upload",
            content_type="multipart/form-data",
            data=data
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data.get("success"))

        download_res = self.client.get(json_data["download_url"])
        self.assertEqual(download_res.status_code, 200)
        self.assertEqual(download_res.mimetype, "application/pdf")


if __name__ == "__main__":
    unittest.main()
