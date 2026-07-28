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
    Convert a Word (.doc / .docx) file into a PDF document.

    Args:
        word_path (str):
            Path to the uploaded Word document.

    Returns:
        tuple:
            (output_filename, output_path)
    """

    if not os.path.exists(word_path):
        raise FileNotFoundError("Word document not found.")

    stem = os.path.splitext(os.path.basename(word_path))[0]
    output_filename = f"{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    # 1. Try docx2pdf if Word COM automation is available
    try:
        from docx2pdf import convert
        convert(word_path, output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_filename, output_path
    except Exception:
        pass

    # 2. Pure-python fallback using python-docx and reportlab
    try:
        import docx
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        doc = docx.Document(word_path)
        pdf_doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(safe_text, styles["Normal"]))
                story.append(Spacer(1, 6))

        if not story:
            story.append(Paragraph(" ", styles["Normal"]))

        pdf_doc.build(story)
        return output_filename, output_path

    except Exception as e:
        raise ValueError(f"Failed to convert Word to PDF: {str(e)}")