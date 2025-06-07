from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

@app.route('/define/<word>')
def define(word):
    text = word.strip()
    if not text:
        return jsonify({"error": "Empty input"}), 400

    # Optional: keep limit param for interface compatibility
    _ = request.args.get('limit', type=int)

    # LibreTranslate API
    try:
        res = requests.post(
            "https://libretranslate.de/translate",
            json={
                "q": text,
                "source": "fr",
                "target": "en",
                "format": "text"
            },
            headers={"Content-Type": "application/json"}
        )
        data = res.json()
        translation = data.get("translatedText")

        if not translation:
            return jsonify({"error": "Translation failed"}), 500

        return jsonify([{
            "french": text,
            "english": translation
        }])

    except Exception as e:
        return jsonify({"error": str(e)}), 500
