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