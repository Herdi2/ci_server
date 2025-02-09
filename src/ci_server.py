import logging
from flask import Flask, request, jsonify
from pathlib import Path
import system_routines, notifier

# Initialize Flask app for webhook handling
app = Flask(__name__)

# Handle incoming webhook requests
@app.route("/update/", methods=["POST"])
def updatehandler():
    """Handles incoming webhook events from GitHub and triggers necessary actions."""
    data = request.get_json()
    
    
    """Run tests"""
    # system_routines.clone_and_run(data)
    # Notify users
    token_path = Path(__file__).parent / "../.token"
    notifier.send_notification("success", 
                               data['repository']['full_name'],
                                # This only checks latest commit in a push
                               data['head_commit']['id'],
                               open(token_path, "r").read(),
                               None) 
    
    
    return jsonify({"message": "Received update, running tests"}), 200



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting CI server...")
    app.run(host="0.0.0.0", port=3200, debug=True)
