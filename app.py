from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import logging

app = Flask(__name__, static_folder="static", static_url_path="")

API_KEY = os.environ.get("API_KEY")
MODEL = "models/gemini-2.0-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent"

if not API_KEY:
    logging.warning("API_KEY environment variable is not set!")


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.json
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"answer": "Please provide a prompt."}), 400

    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": API_KEY
    }
    json_data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(ENDPOINT, headers=headers, params=params, json=json_data, timeout=10)
        response.raise_for_status()
        resp_json = response.json()
        answer = resp_json['candidates'][0]['content']['parts'][0]['text']
        answer = answer.replace("Gemini", "SrujanAI")
        return jsonify({"answer": answer})

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling AI service: {e}")
        return jsonify({"answer": "Error: Could not reach AI service, please try again later."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
