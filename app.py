import os
import psutil
import subprocess
from flask import Flask, render_template

app = Flask(__name__)

SERVICES = {
    "openhands": {
        "name": "OpenHands",
        "command": "cd /home/opc/ai-dashboard/Command-Doc/OpenHands && ./start.sh",
        "port": 3000,
        "pid": None
    },
    "devika": {
        "name": "Devika",
        "command": "cd /home/opc/ai-dashboard/Command-Doc/devika && ./start.sh",
        "port": 3001,
        "pid": None
    },
    "openclaw": {
        "name": "OpenClaw",
        "command": "cd /home/opc/ai-dashboard/Command-Doc/openclaw && ./start.sh",
        "port": 3002,
        "pid": None
    }
}

@app.route('/')
def index():
    return render_template('index.html', services=SERVICES)

@app.route('/start/<service_id>')
def start_service(service_id):
    if service_id in SERVICES:
        # Start a dummy process or the actual service
        print(f"Starting {service_id}")
        # In a real scenario, this would spin up Docker containers
    return render_template('index.html', services=SERVICES)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
