import os
from flask import Flask, render_template

import config
from routes import register_routes

app = Flask(__name__)

# Configure application
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = config.OUTPUT_FOLDER
app.config["TEMP_FOLDER"] = config.TEMP_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.secret_key = config.SECRET_KEY

# Ensure directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
os.makedirs(app.config["TEMP_FOLDER"], exist_ok=True)

# Register route blueprints
register_routes(app)


@app.route("/")
def home():
    """Renders the landing page."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)