import os
import io
import uuid
import shutil
from pypdf import PdfWriter, PdfReader, errors
import config


def merge_pdfs(pdf_paths, output_name=None):
    """
    Merge multiple PDF files into one PDF.
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
    """
    import zipfile
    import tempfile

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


def protect_pdf_file(pdf_path, password, output_name=None):
    """
    Encrypt a PDF file with a user password.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not password:
        raise ValueError("Password cannot be empty.")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"protected_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path


def unlock_pdf_file(pdf_path, password, output_name=None):
    """
    Decrypt a password-protected PDF file.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        if not password:
            raise ValueError("Password is required to unlock this PDF.")
        decrypt_success = reader.decrypt(password)
        if decrypt_success == 0:
            raise ValueError("Incorrect password provided for the encrypted PDF.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"unlocked_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path


def watermark_pdf_file(pdf_path, watermark_text="CONFIDENTIAL", opacity=0.3, rotation=45, output_name=None):
    """
    Overlay a custom text watermark onto all pages of a PDF document.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    from reportlab.pdfgen import canvas

    text = watermark_text.strip() if watermark_text else "CONFIDENTIAL"
    opacity_val = float(opacity)
    rotation_val = int(rotation)

    # Generate watermark overlay PDF in memory
    wm_buf = io.BytesIO()
    c = canvas.Canvas(wm_buf, pagesize=(612, 792))
    c.saveState()
    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0.5, 0.5, 0.5, opacity_val)
    c.translate(306, 396)
    c.rotate(rotation_val)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    wm_buf.seek(0)

    wm_reader = PdfReader(wm_buf)
    watermark_page = wm_reader.pages[0]

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"watermarked_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path


def remove_watermark_file(pdf_path, watermark_text=None, output_name=None):
    """
    Redact and remove watermark text / annotations from a PDF file using PyMuPDF (fitz).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"cleaned_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page in doc:
            if watermark_text and watermark_text.strip():
                text_instances = page.search_for(watermark_text.strip())
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=None)
                page.apply_redactions()

            annots = page.annots()
            if annots:
                for annot in annots:
                    page.delete_annot(annot)

        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        return output_filename, output_path
    except Exception as e:
        raise ValueError(f"Failed to remove watermark: {str(e)}")


def parse_page_selection(selection_input, total_pages):
    """
    Parse page selection input (list, string, or ranges e.g. '1, 3, 5-7') into 1-based page indices.
    """
    selected_pages = []
    if isinstance(selection_input, str):
        items = [x.strip() for x in selection_input.split(",") if x.strip()]
    elif isinstance(selection_input, (list, tuple)):
        items = selection_input
    elif isinstance(selection_input, int):
        items = [selection_input]
    else:
        items = []

    for item in items:
        if isinstance(item, int):
            p = item
            if 1 <= p <= total_pages:
                if p not in selected_pages:
                    selected_pages.append(p)
            else:
                raise ValueError(f"Page number {p} is out of bounds (1-{total_pages}).")
        elif isinstance(item, str):
            item = item.strip()
            if "-" in item:
                parts = item.split("-")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start, end = int(parts[0]), int(parts[1])
                    if start > end:
                        raise ValueError(f"Invalid range '{item}': start page cannot be greater than end page.")
                    if start < 1 or end > total_pages:
                        raise ValueError(f"Range '{item}' is out of bounds (1-{total_pages}).")
                    for p in range(start, end + 1):
                        if p not in selected_pages:
                            selected_pages.append(p)
                else:
                    raise ValueError(f"Invalid page range format: '{item}'")
            elif item.isdigit():
                p = int(item)
                if 1 <= p <= total_pages:
                    if p not in selected_pages:
                        selected_pages.append(p)
                else:
                    raise ValueError(f"Page number {p} is out of bounds (1-{total_pages}).")
            else:
                raise ValueError(f"Invalid page number value: '{item}'")

    return selected_pages


def delete_pages(pdf_path, pages_to_delete, output_name=None):
    """
    Delete specified pages from a PDF document.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("PDF file contains no pages.")

    to_delete = set(parse_page_selection(pages_to_delete, total_pages))
    if not to_delete:
        raise ValueError("No valid pages selected for deletion.")

    if len(to_delete) >= total_pages:
        raise ValueError("Cannot delete all pages from the PDF.")

    writer = PdfWriter()
    for idx, page in enumerate(reader.pages, start=1):
        if idx not in to_delete:
            writer.add_page(page)

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"deleted_pages_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path


def extract_pages(pdf_path, pages_to_extract, output_name=None):
    """
    Extract specified pages from a PDF document into a new PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("PDF file contains no pages.")

    to_extract = parse_page_selection(pages_to_extract, total_pages)
    if not to_extract:
        raise ValueError("No valid pages selected for extraction.")

    writer = PdfWriter()
    for p in to_extract:
        writer.add_page(reader.pages[p - 1])

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"extracted_pages_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path


def reorder_pages(pdf_path, page_order, output_name=None):
    """
    Reorder pages of a PDF according to the given order list (1-based indices).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("PDF file contains no pages.")

    if isinstance(page_order, str):
        import json
        try:
            page_order = json.loads(page_order)
        except Exception:
            page_order = [int(x.strip()) for x in page_order.split(",") if x.strip().isdigit()]

    if not isinstance(page_order, (list, tuple)) or not page_order:
        raise ValueError("Invalid page order provided.")

    validated_order = []
    for p in page_order:
        p_int = int(p)
        if 1 <= p_int <= total_pages:
            validated_order.append(p_int)
        else:
            raise ValueError(f"Page number {p_int} is out of bounds (1-{total_pages}).")

    if not validated_order:
        raise ValueError("No valid page numbers found in order list.")

    writer = PdfWriter()
    for p in validated_order:
        writer.add_page(reader.pages[p - 1])

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"reordered_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path


def add_page_numbers(pdf_path, position="bottom-right", format_str="Page {page} of {total}", start_page=1, font_size=10, output_name=None):
    """
    Add customizable page numbers to each page of a PDF document.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    from reportlab.pdfgen import canvas

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("PDF file contains no pages.")

    start_pg = int(start_page) if str(start_page).isdigit() else 1
    font_sz = int(font_size) if str(font_size).isdigit() else 10

    writer = PdfWriter()

    for idx, page in enumerate(reader.pages, start=1):
        if idx < start_pg:
            writer.add_page(page)
            continue

        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        # Generate overlay for this page
        overlay_buf = io.BytesIO()
        c = canvas.Canvas(overlay_buf, pagesize=(width, height))
        c.setFont("Helvetica", font_sz)
        c.setFillColorRGB(0.2, 0.2, 0.2)

        page_num_str = format_str.format(page=idx - start_pg + 1, total=total_pages - start_pg + 1)

        margin = 30
        pos = position.lower()
        if "top" in pos:
            y = height - margin
        else:
            y = margin

        if "left" in pos:
            c.drawString(margin, y, page_num_str)
        elif "center" in pos:
            c.drawCentredString(width / 2.0, y, page_num_str)
        else:  # right
            c.drawRightString(width - margin, y, page_num_str)

        c.save()
        overlay_buf.seek(0)

        overlay_reader = PdfReader(overlay_buf)
        overlay_page = overlay_reader.pages[0]

        page.merge_page(overlay_page)
        writer.add_page(page)

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = output_name or f"numbered_{stem}.pdf"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_filename, output_path