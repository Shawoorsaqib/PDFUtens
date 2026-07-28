# PDFUtens

**PDFUtens** is a modern, fast, and secure web application providing a full suite of PDF manipulation and conversion tools.

---

## Features & Tools Catalog

### 1. Convert to PDF
- **Image to PDF**: Convert JPG, PNG, JPEG, and WEBP images into high-quality PDFs.
- **Word to PDF**: Convert Microsoft Word (.docx and .doc) documents into clean PDF files.

### 2. Convert from PDF
- **PDF to Word**: Convert PDF files into fully editable Microsoft Word (.docx) documents.

### 3. Organize PDF
- **Merge PDF**: Combine multiple PDF documents into a single organized PDF.
- **Split PDF**: Extract page ranges or split a PDF into individual page files.

### 4. Edit PDF
- **Rotate PDF**: Rotate PDF pages 90°, 180°, or 270° clockwise with real-time visual canvas preview.

### 5. PDF Security & Optimization
- **Compress PDF**: Optimize content streams and compress image streams to reduce PDF file size.

---

## Installation & Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shawoorsaqib/PDFUtens.git
   cd PDFUtens
   ```

2. **Set Up Environment & Dependencies**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`.

---

## Automated Test Suite

Run the full automated unit test suite:

```bash
.venv\Scripts\python.exe -m unittest discover tests
```

---

## Technology Stack
- **Backend**: Python 3.x, Flask (Modular Blueprints)
- **PDF & Document Processing**: `pypdf`, `pymupdf` (fitz), `pdf2docx`, `docx2pdf`, `python-docx`, `reportlab`, `Pillow`
- **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6+), PDF.js, Bootstrap Icons
