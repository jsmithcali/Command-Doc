from flask import Flask, render_template, request, jsonify
import os
import subprocess
import signal
import psutil
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = {
    "openhands": {
        "port": 3000, 
        "status": "offline", 
        "dir": "OpenHands", 
        "command": ["docker", "compose", "up", "-d"],
        "stop_cmd": ["docker", "compose", "down"],
    },
    "devika": {
        "port": 3001, 
        "status": "offline", 
        "dir": "devika", 
        "command": ["python3", "devika.py"],
    },
    "openclaw": {
        "port": 3002, 
        "status": "offline", 
        "dir": "openclaw", 
        "command": ["npm", "start"],
    }
}

processes = {}

def is_port_in_use(port):
    for conn in psutil.net_connections():
        if conn.status == 'LISTEN' and conn.laddr.port == port:
            return True
    return False

def get_service_status(service_name):
    service = SERVICES.get(service_name)
    if not service:
        return "unknown"
    port = service["port"]
    if is_port_in_use(port):
        return "online"
    return "offline"

@app.route("/")
def index():
    status_map = {}
    for name in SERVICES:
        status_map[name] = get_service_status(name)
    return render_template("index.html", services=SERVICES, status_map=status_map,
                           gemini_key=os.getenv("GEMINI_API_KEY", ""),
                           google_account=os.getenv("GOOGLE_ACCOUNT", ""))

@app.route("/status")
def all_status():
    status_map = {}
    for name in SERVICES:
        status_map[name] = get_service_status(name)
    return jsonify(status_map)

@app.route("/status/<service_name>")
def service_status(service_name):
    if service_name not in SERVICES:
        return jsonify({"error": "Invalid service name"}), 400
    return jsonify({"status": get_service_status(service_name)})

@app.route("/start/<service_name>", methods=["POST"])
def start_service(service_name):
    if service_name not in SERVICES:
        return jsonify({"error": "Invalid service name"}), 400
    
    service = SERVICES[service_name]
    service_dir = os.path.join(BASE_DIR, service["dir"])
    
    current_status = get_service_status(service_name)
    if current_status == "online":
        return jsonify({"message": f"{service_name} is already running"}), 200
    
    try:
        proc = subprocess.Popen(
            service["command"],
            cwd=service_dir,
            stdout=open(f"/tmp/{service_name}_stdout.log", "a"),
            stderr=open(f"/tmp/{service_name}_stderr.log", "a"),
            preexec_fn=os.setsid
        )
        processes[service_name] = proc
        return jsonify({"message": f"{service_name} started successfully", "status": "online"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stop/<service_name>", methods=["POST"])
def stop_service(service_name):
    if service_name not in SERVICES:
        return jsonify({"error": "Invalid service name"}), 400
    
    if service_name in processes:
        proc = processes[service_name]
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            del processes[service_name]
        except:
            pass
    
    return jsonify({"message": f"{service_name} stopped successfully", "status": "offline"}), 200

@app.route("/logs/<service_name>")
def service_logs(service_name):
    if service_name not in SERVICES:
        return jsonify({"error": "Invalid service name"}), 400
    
    stdout_log = f"/tmp/{service_name}_stdout.log"
    stderr_log = f"/tmp/{service_name}_stderr.log"
    
    logs = ""
    if os.path.exists(stdout_log):
        with open(stdout_log, "r") as f:
            logs += "=== STDOUT ===\n" + f.read()[-5000:]
    if os.path.exists(stderr_log):
        with open(stderr_log, "r") as f:
            logs += "\n=== STDERR ===\n" + f.read()[-5000:]
    
    return jsonify({"logs": logs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)