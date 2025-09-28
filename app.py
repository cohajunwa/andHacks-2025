import os
import logging
import json
import datetime

from flask import Flask, request, render_template

app = Flask(__name__, template_folder="frontend", static_folder="frontend", static_url_path="" )
app.logger.setLevel(logging.DEBUG) 


UPLOAD_FOLDER = "assets/images"
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

def process_timestamp(timestamp):
        # Timestamp currently in ms since Unix epoch
    try:
        
        ts_seconds = timestamp / 1000  
        
        dt = datetime.datetime.fromtimestamp(ts_seconds) # Gives local time (may want to use UTC in the future)
        app.logger.warning(dt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception :
        return timestamp
        
def store_img_metadata_as_json(id: str, request_form_data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)

    img_metadata = {}
    if "id" in request_form_data:
        img_metadata["id"] = request_form_data["id"]
    if "latitude" in request_form_data and request_form_data["latitude"] != "null":
        img_metadata["latitude"] = float(request_form_data["latitude"])
    if "longitude" in request_form_data and request_form_data["longitude"] != "null":
        img_metadata["longitude"] = float(request_form_data["longitude"])
    if "timestamp" in request_form_data and request_form_data["timestamp"] != "null":
        img_metadata["timestamp"] = int(request_form_data["timestamp"])
        img_metadata["local_time"] = process_timestamp(img_metadata["timestamp"])
    if "description" in request_form_data and request_form_data["description"] != "null":
        img_metadata["description"] = request_form_data["description"] 

    save_file = os.path.join(DATA_DIR, f"{id}.json")

    with open(save_file, "w") as file:
        json.dump(img_metadata, file)



if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True)
