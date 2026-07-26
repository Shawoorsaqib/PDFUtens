from flask import Flask, render_template
import os

from routes.image_to_pdf import image_to_pdf_bp

import config


app = Flask(__name__)
app.register_blueprint(image_to_pdf_bp)

app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = config.OUTPUT_FOLDER
app.config["TEMP_FOLDER"] = config.TEMP_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.secret_key = config.SECRET_KEY

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
os.makedirs(app.config["TEMP_FOLDER"], exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)