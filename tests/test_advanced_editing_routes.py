import os
import io
import unittest
from pypdf import PdfWriter, PdfReader

from app import app


def create_test_pdf(num_pages=5):
    """Utility helper to generate a sample multi-page PDF in memory."""
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612, 792))
    for i in range(1, num_pages + 1):
        c.setFont("Helvetica", 24)
        c.drawString(100, 700, f"Test Page {i}")
        c.showPage()
    c.save()
    buf.seek(0)
    return buf


class TestAdvancedEditingRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_get_advanced_editing_views(self):
        """Test GET requests for all four advanced editing views."""
        routes = ["/delete-pages", "/extract-pages", "/reorder-pages", "/add-page-numbers"]
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Failed GET for {route}")
            self.assertIn(b"<html", response.data.lower())

    def test_delete_pages_upload_success(self):
        """Test POST upload for Delete Pages."""
        pdf_buf = create_test_pdf(5)
        data = {
            "file": (pdf_buf, "sample.pdf"),
            "pages": "2, 4"
        }
        response = self.client.post(
            "/delete-pages/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertTrue(res_json["success"])
        self.assertIn("download_url", res_json)

        # Test download endpoint
        filename = res_json["filename"]
        dl_res = self.client.get(f"/delete-pages/download/{filename}")
        self.assertEqual(dl_res.status_code, 200)
        self.assertEqual(dl_res.mimetype, "application/pdf")

        # Verify page count is 3 (5 - 2 = 3)
        reader = PdfReader(io.BytesIO(dl_res.data))
        self.assertEqual(len(reader.pages), 3)

    def test_extract_pages_upload_success(self):
        """Test POST upload for Extract Pages."""
        pdf_buf = create_test_pdf(5)
        data = {
            "file": (pdf_buf, "sample.pdf"),
            "pages": "1, 3-4"
        }
        response = self.client.post(
            "/extract-pages/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertTrue(res_json["success"])

        # Test download endpoint
        filename = res_json["filename"]
        dl_res = self.client.get(f"/extract-pages/download/{filename}")
        self.assertEqual(dl_res.status_code, 200)

        # Verify extracted page count is 3
        reader = PdfReader(io.BytesIO(dl_res.data))
        self.assertEqual(len(reader.pages), 3)

    def test_reorder_pages_upload_success(self):
        """Test POST upload for Reorder Pages."""
        pdf_buf = create_test_pdf(3)
        data = {
            "file": (pdf_buf, "sample.pdf"),
            "order": "3, 1, 2"
        }
        response = self.client.post(
            "/reorder-pages/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertTrue(res_json["success"])

        # Test download endpoint
        filename = res_json["filename"]
        dl_res = self.client.get(f"/reorder-pages/download/{filename}")
        self.assertEqual(dl_res.status_code, 200)

        # Verify reordered page count is 3
        reader = PdfReader(io.BytesIO(dl_res.data))
        self.assertEqual(len(reader.pages), 3)

    def test_add_page_numbers_upload_success(self):
        """Test POST upload for Add Page Numbers."""
        pdf_buf = create_test_pdf(2)
        data = {
            "file": (pdf_buf, "sample.pdf"),
            "position": "bottom-right",
            "format": "Page {page} of {total}",
            "start_page": "1",
            "font_size": "12"
        }
        response = self.client.post(
            "/add-page-numbers/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertTrue(res_json["success"])

        # Test download endpoint
        filename = res_json["filename"]
        dl_res = self.client.get(f"/add-page-numbers/download/{filename}")
        self.assertEqual(dl_res.status_code, 200)

        reader = PdfReader(io.BytesIO(dl_res.data))
        self.assertEqual(len(reader.pages), 2)

    def test_invalid_page_range_errors(self):
        """Test error handling when out of bounds or invalid inputs are provided."""
        pdf_buf = create_test_pdf(3)

        # Deleting out-of-bounds page number
        pdf_buf1 = create_test_pdf(3)
        response = self.client.post(
            "/delete-pages/upload",
            data={"file": (pdf_buf1, "sample.pdf"), "pages": "10"},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

        # Extracting out-of-bounds page range
        pdf_buf2 = create_test_pdf(3)
        response = self.client.post(
            "/extract-pages/upload",
            data={"file": (pdf_buf2, "sample.pdf"), "pages": "2-15"},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_range_string_delete_and_extract(self):
        """Test page range strings like '2-4' for deleting and extracting pages."""
        pdf_buf = create_test_pdf(10)
        response = self.client.post(
            "/extract-pages/upload",
            data={"file": (pdf_buf, "sample.pdf"), "pages": "6-8"},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertTrue(res_json["success"])

        filename = res_json["filename"]
        dl_res = self.client.get(f"/extract-pages/download/{filename}")
        self.assertEqual(dl_res.status_code, 200)
        reader = PdfReader(io.BytesIO(dl_res.data))
        # Pages 6, 7, 8 -> exactly 3 pages
        self.assertEqual(len(reader.pages), 3)


if __name__ == "__main__":
    unittest.main()
