
from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)

STATUS_FILE = "../ai/status.json"

@app.route("/")
def index():
    return render_template("status.html")

@app.route("/status")
def get_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)
        return jsonify(status)
    else:
        return jsonify({"status": "🤖 Bot not running or no status available."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
