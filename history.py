import os
import json
from datetime import datetime
from settings import SETTINGS_DIR

HISTORY_PATH = os.path.join(SETTINGS_DIR, "history.json")

def load_history(path=HISTORY_PATH):
    '''Loads the history from path, or returns an empty list if it does not exist.'''
    try:
        with open(path) as json_file:
            data = json.load(json_file)
    except (OSError, ValueError):
        data = []
    return data if isinstance(data, list) else []

def save_to_history(model:str, prompt:str, body:str, response:str, path=HISTORY_PATH):
    '''Adds a new request and response to the history at path.'''
    log = load_history(path)
    log.append({"Time": datetime.now().isoformat(timespec="seconds"),
                "Model": model,
                "Prompt": prompt,
                "Email": body,
                "Response": response})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as outfile:
        json.dump(log, outfile, indent=2)
