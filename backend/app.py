from flask import Flask, request, jsonify
import requests
import json
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")
PINATA_BASE_URL = "https://api.pinata.cloud/"


def upload_image_to_pinata(file):
    url = PINATA_BASE_URL + "pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    files = {
        'file': (secure_filename(file.filename), file.stream, file.content_type)
    }
    response = requests.post(url, files=files, headers=headers)
    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    else:
        raise Exception("Image upload failed: " + response.text)


def upload_json_to_pinata(json_data):
    url = PINATA_BASE_URL + "pinning/pinJSONToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(json_data), headers=headers)
    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    else:
        raise Exception("JSON upload failed: " + response.text)


@app.route("/upload_profile", methods=["POST"])
def upload_profile():
    try:
        name = request.form.get("name")
        bio = request.form.get("bio")
        country = request.form.get("country")
        email = request.form.get("email")
        image = request.files.get("image")

        if not all([name, bio, image]):
            return jsonify({"error": "Missing required fields"}), 400

        # Upload image
        image_url = upload_image_to_pinata(image)

        # Create metadata
        metadata = {
            "name": name,
            "bio": bio,
            "country": country,
            "email": email,
            "image": image_url
        }

        # Upload metadata to IPFS
        metadata_uri = upload_json_to_pinata(metadata)

        return jsonify({"tokenURI": metadata_uri})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
