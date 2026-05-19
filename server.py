from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import os
import socket

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'mobile_controller'), static_url_path='')
CORS(app)  # Allow mobile browser to send requests

# Shared data between Flask and game loop (protected by a lock)
current_command = {"action": None}
command_lock = threading.Lock()

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Connect to a public DNS server (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route('/')
def serve_index():
    """Serve the mobile controller index.html"""
    return send_file(os.path.join(os.path.dirname(__file__), 'mobile_controller', 'index.html'))

@app.route('/server-info', methods=['GET'])
def server_info():
    """Return server IP and port info for auto-connection"""
    return jsonify({
        "ip": get_local_ip(),
        "port": 3000,
        "url": f"http://{get_local_ip()}:3000"
    }), 200

@app.route('/command', methods=['GET'])
def handle_command():
    """Receive command from mobile device."""
    move = request.args.get('move', '').lower()
    valid_commands = ['forward', 'backward', 'left', 'right', 'stop', 'faster', 'slower']
    if move in valid_commands:
        with command_lock:
            current_command["action"] = move
        return jsonify({"status": "ok", "command": move}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid command"}), 400

def get_command():
    """Thread-safe read of the latest command."""
    with command_lock:
        return current_command["action"]