from PIL import Image
import os

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