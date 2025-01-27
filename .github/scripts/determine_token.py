import os
import json
from datetime import datetime

TOKEN_1 = os.environ.get("X_BEARER_TOKEN_1", "")
TOKEN_2 = os.environ.get("X_BEARER_TOKEN_2", "")
TOKEN_3 = os.environ.get("X_BEARER_TOKEN_3", "")

tokens = [t for t in [TOKEN_1, TOKEN_2, TOKEN_3] if t]  # Keep only non-empty tokens

rotation_file = "state/token-rotation.json"
today_str = datetime.now().strftime("%Y-%m-%d")

today_str = datetime.now().strftime("%Y-%m-%d")

if os.path.exists(rotation_file):
    with open(rotation_file, 'r') as f:
        rotation_state = json.load(f)
else:
    rotation_state = {
        "date": today_str,
        "index": 0
    }

if rotation_state["date"] != today_str:
    rotation_state["date"] = today_str
    rotation_state["index"] = 0

current_index = rotation_state["index"]
if current_index < len(tokens):
    used_token = tokens[current_index]
    rotation_state["index"] += 1
else:
    # No more tokens available
    used_token = ""

with open(rotation_file, 'w') as f:
    json.dump(rotation_state, f)

print(f"::set-output name=token::{used_token}")