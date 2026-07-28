from .image_to_pdf import image_to_pdf_bp
from .merge_pdf import merge_pdf_bp
from .compress_pdf import compress_pdf_bp
from .pdf_to_word import pdf_to_word_bp
from .rotate_pdf import rotate_pdf_bp
from .split_pdf import split_pdf_bp
from .word_to_pdf import word_to_pdf_bp
from .tools import tools_bp
from .api import api_bp


def register_routes(app):
    """
    Register all application blueprints.
    """
    app.register_blueprint(image_to_pdf_bp)
    app.register_blueprint(merge_pdf_bp)
    app.register_blueprint(compress_pdf_bp)
    app.register_blueprint(pdf_to_word_bp)
    app.register_blueprint(rotate_pdf_bp)
    app.register_blueprint(split_pdf_bp)
    app.register_blueprint(word_to_pdf_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(api_bp)