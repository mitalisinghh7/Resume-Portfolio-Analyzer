import json
import os
from datetime import datetime

HISTORY_FILE = "analysis_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def update_last_analysis(username):
    history = load_history()
    current_time = datetime.now().strftime("%B %d, %Y | %I:%M %p")
    history[username] = current_time
    save_history(history)
    return current_time

def get_last_analysis(username):
    history = load_history()
    return history.get(username, "No previous analysis found.")