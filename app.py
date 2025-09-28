import os
import logging
import json

from flask import Flask, request, render_template

app = Flask(__name__, template_folder="frontend", static_folder="frontend", static_url_path="" )
app.logger.setLevel(logging.DEBUG) 


UPLOAD_FOLDER = "IMAGES/"
DATA_DIR = 'DATA/'

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

    id = request.form["id"]
    store_img_metadata_as_json(id, request.form)

    return {"status": "ok"}

def store_img_metadata_as_json(id: str, img_metadata: dict):
    os.makedirs(DATA_DIR, exist_ok=True)

    # TODO: Add error handling
    json_data = json.dumps(img_metadata)

    save_file = os.path.join(DATA_DIR, f"{id}.json")

    with open(save_file, "w") as file:
        json.dump(json_data, file)



if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True)
