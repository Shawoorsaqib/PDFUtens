import os
import uuid
from pypdf import PdfWriter, errors
import config


def merge_pdfs(pdf_paths, output_name=None):
    """
    Merge multiple PDF files into one PDF.

    Args:
        pdf_paths (list): List of PDF file paths to merge.
        output_name (str, optional): Custom name for the output PDF.

    Returns:
        tuple: (output_filename, output_path)

    Raises:
        ValueError: If fewer than 2 files are provided.
        FileNotFoundError: If any of the input files do not exist.
    """
    if not pdf_paths or len(pdf_paths) < 2:
        raise ValueError("At least two PDF files are required to merge.")

    merger = PdfWriter()

    try:
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            try:
                merger.append(pdf_path)
            except Exception as e:
                raise ValueError(f"Failed to process PDF '{os.path.basename(pdf_path)}': {str(e)}")

        if output_name:
            output_filename = output_name if output_name.lower().endswith(".pdf") else f"{output_name}.pdf"
        else:
            output_filename = f"merged_{uuid.uuid4().hex[:12]}.pdf"

        output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
        merger.write(output_path)

        return output_filename, output_path

    finally:
        merger.close()