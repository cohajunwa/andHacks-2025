import os
import logging

from flask import Flask, request, render_template
from process_image import process_img, extract_exif_data_from_img

app = Flask(__name__, template_folder="frontend", static_folder="frontend", static_url_path="" )
app.logger.setLevel(logging.DEBUG) 
UPLOAD_FOLDER = "IMAGES/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods = ["POST"])
def upload():
    if "photo" not in request.files:
        app.logger.warning("No photo uploaded")
        return "No photo", 400

    file = request.files["photo"]
    if not file.filename:
        return "Empty filename", 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    result = process_img(file_path)

    app.logger.warning(extract_exif_data_from_img(file_path))

    return {"status": "ok", "result": result}



if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True)
