from PIL import Image
import os
import uuid
from pdf2docx import Converter

import config


def image_to_pdf(image_path):
    """
    Converts an image into a PDF.

    Returns:
        output_filename
        output_path
    """

    image = Image.open(image_path)

    if image.mode != "RGB":
        image = image.convert("RGB")

    filename = os.path.splitext(
        os.path.basename(image_path)
    )[0]

    output_filename = f"{filename}.pdf"

    output_path = os.path.join(
        config.OUTPUT_FOLDER,
        output_filename
    )

    image.save(output_path, "PDF")

    return output_filename, output_path


def images_to_pdf(image_paths, output_name=None):
    """
    Converts one or multiple images into a single PDF.
    """
    if not image_paths:
        return None, None

    images = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    if not output_name:
        first_basename = os.path.splitext(os.path.basename(image_paths[0]))[0]
        output_filename = f"{first_basename}_converted.pdf"
    else:
        output_filename = output_name if output_name.lower().endswith(".pdf") else f"{output_name}.pdf"

    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    first_image = images[0]
    rest_images = images[1:]
    first_image.save(output_path, "PDF", save_all=True, append_images=rest_images)

    return output_filename, output_path


def pdf_to_word(pdf_path):
    """
    Convert a PDF file into a Word (.docx) document.

    Args:
        pdf_path (str):
            Path to the uploaded PDF.

    Returns:
        tuple:
            output_filename,
            output_path
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            "PDF file not found."
        )

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = f"{stem}.docx"

    output_path = os.path.join(
        config.OUTPUT_FOLDER,
        output_filename
    )

    converter = Converter(pdf_path)

    try:
        converter.convert(output_path)
    except Exception as e:
        raise ValueError(
            f"Failed to convert PDF: {str(e)}"
        )
    finally:
        converter.close()

    return output_filename, output_path


def word_to_pdf(word_path):
    """
    Convert a Word (.doc / .docx) file into a PDF document using multi-tier strategies:
    1. MS Word COM Automation (win32com) with pythoncom.CoInitialize()
    2. docx2pdf library with pythoncom.CoInitialize()
    3. LibreOffice / soffice CLI headless conversion
    4. Pure-python fallback (python-docx + reportlab) with table & character sanitization
    5. Plain text extraction fallback
    """
    import shutil
    import subprocess

    if not os.path.exists(word_path):
        raise FileNotFoundError("Word document not found.")

    stem = os.path.splitext(os.path.basename(word_path))[0]
    output_filename = f"{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    # Clean up target output file if it already exists
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass

    # Tier 1: MS Word COM Automation via win32com (Windows)
    try:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False

            abs_in = os.path.abspath(word_path)
            abs_out = os.path.abspath(output_path)

            doc = word.Documents.Open(abs_in, ReadOnly=True)
            # 17 = wdFormatPDF
            doc.SaveAs(abs_out, FileFormat=17)
            doc.Close(False)
            word.Quit()

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_filename, output_path
        finally:
            pythoncom.CoUninitialize()
    except Exception as e:
        print(f"[Word2PDF] win32com attempt skipped/failed: {e}")

    # Tier 2: docx2pdf with CoInitialize
    try:
        import pythoncom
        from docx2pdf import convert
        pythoncom.CoInitialize()
        try:
            convert(word_path, output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_filename, output_path
        finally:
            pythoncom.CoUninitialize()
    except Exception as e:
        print(f"[Word2PDF] docx2pdf attempt skipped/failed: {e}")

    # Tier 3: LibreOffice CLI (soffice)
    try:
        soffice_cmd = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice_cmd:
            subprocess.run([
                soffice_cmd, "--headless", "--convert-to", "pdf",
                "--outdir", config.OUTPUT_FOLDER, word_path
            ], capture_output=True, text=True, timeout=30)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_filename, output_path
    except Exception as e:
        print(f"[Word2PDF] LibreOffice attempt skipped/failed: {e}")

    # Tier 4: Pure-python python-docx + ReportLab
    try:
        import docx
        from docx.oxml.table import CT_Tbl
        from docx.oxml.text.paragraph import CT_P
        from docx.table import Table
        from docx.text.paragraph import Paragraph as DocxParagraph

        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph as RLParagraph, Spacer, Table as RLTable, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        def clean_xml_text(text):
            if not text:
                return ""
            cleaned = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", str(text))
            return cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").strip()

        doc = docx.Document(word_path)
        pdf_doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        heading_style = styles["Heading1"]

        story = []

        # Iterate over body elements (paragraphs & tables in document order)
        for element in doc.element.body:
            if isinstance(element, CT_P):
                p = DocxParagraph(element, doc)
                text = clean_xml_text(p.text)
                if text:
                    style_name = p.style.name.lower() if p.style else ""
                    if "heading" in style_name or "title" in style_name:
                        story.append(RLParagraph(text, heading_style))
                    else:
                        story.append(RLParagraph(text, normal_style))
                    story.append(Spacer(1, 6))
            elif isinstance(element, CT_Tbl):
                tbl = Table(element, doc)
                table_data = []
                for row in tbl.rows:
                    row_data = []
                    for cell in row.cells:
                        cell_text = clean_xml_text(cell.text)
                        row_data.append(RLParagraph(cell_text or " ", normal_style))
                    table_data.append(row_data)

                if table_data:
                    rl_tbl = RLTable(table_data)
                    rl_tbl.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]))
                    story.append(rl_tbl)
                    story.append(Spacer(1, 8))

        if not story:
            story.append(RLParagraph("Word document contains no extractable text.", normal_style))

        pdf_doc.build(story)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_filename, output_path

    except Exception as e:
        print(f"[Word2PDF] python-docx + ReportLab attempt failed: {e}")

    # Tier 5: Plain text extraction fallback
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph as RLParagraph
        from reportlab.lib.styles import getSampleStyleSheet

        raw_bytes = ""
        try:
            with open(word_path, "rb") as f:
                raw_bytes = f.read().decode("utf-8", errors="ignore")
        except Exception:
            raw_bytes = "Converted Document"

        words = re.findall(r"[\x20-\x7E]{3,}", raw_bytes)
        text_content = " ".join(words[:500]) if words else "Converted Word Document"

        pdf_doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        clean_text = text_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story = [RLParagraph(clean_text, styles["Normal"])]
        pdf_doc.build(story)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_filename, output_path

    except Exception as e:
        raise ValueError(f"Failed to convert Word to PDF: {str(e)}")

    raise ValueError("Word to PDF conversion failed. Please verify the uploaded file.")