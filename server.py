from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'mobile_controller'), static_url_path='')
CORS(app)  # Allow mobile browser to send requests

# Shared data between Flask and game loop (protected by a lock)
current_command = {"action": None}
command_lock = threading.Lock()

@app.route('/')
def serve_index():
    """Serve the mobile controller index.html"""
    return send_file(os.path.join(os.path.dirname(__file__), 'mobile_controller', 'index.html'))

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