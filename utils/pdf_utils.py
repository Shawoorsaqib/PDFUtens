import os
import uuid
from pypdf import PdfWriter, PdfReader, errors
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


def split_pdf(pdf_path, split_mode="all", ranges=None, output_folder=None):
    """
    Split a PDF into individual single-page PDF files or extracted page ranges.

    Args:
        pdf_path (str): Path to the input PDF.
        split_mode (str): 'all' (split every page) or 'range' (extract custom page ranges).
        ranges (list, optional): List of dicts like [{'from': 1, 'to': 3}, ...] or tuples (start, end).
        output_folder (str, optional): Custom folder where output will be written.

    Returns:
        tuple: (output_filename, output_path) - a ZIP file if multiple PDFs created, or a single PDF file.

    Raises:
        FileNotFoundError: If input PDF does not exist.
        ValueError: If PDF cannot be read or range values are invalid.
    """
    import zipfile
    import tempfile
    import shutil

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        if total_pages == 0:
            raise ValueError("The provided PDF file contains no pages.")
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}")

    temp_dir = tempfile.mkdtemp(prefix="split_work_")

    try:
        generated_files = []

        if split_mode == "range" and ranges:
            normalized_ranges = []
            for item in ranges:
                if isinstance(item, dict):
                    start = int(item.get("from", item.get("start", 1)))
                    end = int(item.get("to", item.get("end", start)))
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    start, end = int(item[0]), int(item[1])
                else:
                    continue

                if start < 1 or end > total_pages:
                    raise ValueError(f"Page range ({start}-{end}) is out of bounds (1-{total_pages}).")
                if start > end:
                    raise ValueError(f"Start page ({start}) cannot be greater than end page ({end}).")

                normalized_ranges.append((start, end))

            if not normalized_ranges:
                raise ValueError("No valid page ranges provided.")

            for index, (start, end) in enumerate(normalized_ranges, start=1):
                writer = PdfWriter()
                for pg_num in range(start - 1, end):
                    writer.add_page(reader.pages[pg_num])

                if start == end:
                    out_name = f"page_{start}.pdf"
                else:
                    out_name = f"pages_{start}_to_{end}.pdf"

                out_path = os.path.join(temp_dir, out_name)
                with open(out_path, "wb") as f:
                    writer.write(f)
                writer.close()
                generated_files.append((out_name, out_path))

        else:
            # Default: split every page
            for pg_num, page in enumerate(reader.pages, start=1):
                writer = PdfWriter()
                writer.add_page(page)
                out_name = f"page_{pg_num}.pdf"
                out_path = os.path.join(temp_dir, out_name)
                with open(out_path, "wb") as f:
                    writer.write(f)
                writer.close()
                generated_files.append((out_name, out_path))

        dest_folder = output_folder or config.OUTPUT_FOLDER
        os.makedirs(dest_folder, exist_ok=True)

        if len(generated_files) == 1:
            out_name, single_path = generated_files[0]
            output_filename = f"split_{uuid.uuid4().hex[:12]}_{out_name}"
            final_path = os.path.join(dest_folder, output_filename)
            shutil.copy(single_path, final_path)
            return output_filename, final_path
        else:
            output_filename = f"split_{uuid.uuid4().hex[:12]}.zip"
            final_path = os.path.join(dest_folder, output_filename)
            with zipfile.ZipFile(final_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for out_name, file_path in generated_files:
                    zf.write(file_path, arcname=out_name)
            return output_filename, final_path

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def compress_pdf_file(pdf_path, output_name=None):
    """
    Compress content streams & image garbage collection of a PDF file to reduce size.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    try:
        import fitz
        doc = fitz.open(pdf_path)
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        return output_filename, output_path
    except Exception:
        pass

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path


def rotate_pdf_file(pdf_path, rotation_angle=90, output_name=None):
    """
    Rotate all pages of a PDF file by specified angle (90, 180, 270).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    angle = int(rotation_angle) % 360

    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path