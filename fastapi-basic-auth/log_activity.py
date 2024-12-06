import json
from datetime import datetime
import os

def log_event(event: str, username: str, status: str):
    log = {
        "event": event,
        "username": username,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    if os.path.exists("logs.json"):
        with open("logs.json", "r") as file:
            logs = json.load(file)
    else:
        logs = []
    
    logs.append(log)
    
    with open("logs.json", "w") as file:
        json.dump(logs, file, indent=4)
