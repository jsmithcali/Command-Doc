from flask import Flask, render_template, request, jsonify
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SERVICES = {
    "openhands": {"port": 3000, "status": "offline", "dir": "OpenHands", "command": "make run"},
    "devika": {"port": 3001, "status": "offline", "dir": "devika", "command": "python3 devika.py"},
    "openclaw": {"port": 3002, "status": "offline", "dir": "openclaw", "command": "npm start"}
}

@app.route("/")
def index():
    return render_template("index.html", services=SERVICES,
                           gemini_key=os.getenv("GEMINI_API_KEY", ""),
                           google_account=os.getenv("GOOGLE_ACCOUNT", ""))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
