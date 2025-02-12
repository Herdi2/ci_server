import logging
from flask import Flask, request, jsonify
from pathlib import Path
import history
import webhook_handler as handler

# Initialize Flask app for webhook handling
app = Flask(__name__)

# Handle incoming webhook requests
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Handles incoming webhook events from GitHub and triggers necessary actions."""
    data = request.get_json()
    
    """Run tests"""
    # system_routines.clone_and_run(data)
    # Notify users
    event_type = request.headers.get("X-GitHub-Event", "Unknown")
    if event_type == "push":
        token_path = Path(__file__).parent / "../.token"
        handler.handle_push_event(data, open(token_path, "r").read())
    
    return jsonify({"message": "Received update, running tests"}), 200
@app.route("/history")
def show_history():
    data = history.read_history()
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting CI server...")
    app.run(host="0.0.0.0", port=3200, debug=True)
