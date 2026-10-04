import os
import json

# stored in the user's home folder (not the project folder) so the key is never committed to git
SETTINGS_DIR = os.path.join(os.path.expanduser("~"), ".ai-email-enhancer")
SETTINGS_PATH = os.path.join(SETTINGS_DIR, "settings.json")

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_PROMPT = ("Creatively improve the English in the following email. "
                  "Reply with the improved email only.")
DEFAULTS = {"api_key": "", "model": DEFAULT_MODEL, "prompt": DEFAULT_PROMPT, "save_history": False}

def load_settings(path=SETTINGS_PATH):
    '''Loads settings from path. Missing file or missing fields fall back to defaults.'''
    settings = dict(DEFAULTS)
    try:
        with open(path) as json_file:
            saved = json.load(json_file)
    except (OSError, ValueError):
        saved = {}
    if isinstance(saved, dict):
        settings.update({k: v for k, v in saved.items()
                         if k in DEFAULTS and type(v) is type(DEFAULTS[k])})
    # fall back to the environment variable if no key has been saved
    if not settings["api_key"]:
        settings["api_key"] = os.environ.get("OPENAI_API_KEY", "")
    if not settings["model"].strip():
        settings["model"] = DEFAULT_MODEL
    if not settings["prompt"].strip():
        settings["prompt"] = DEFAULT_PROMPT
    return settings

def save_settings(api_key:str, model:str, prompt:str, save_history:bool, path=SETTINGS_PATH):
    '''Saves the settings to path.'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    settings = {"api_key": api_key.strip(),
                "model": model.strip(),
                "prompt": prompt.strip(),
                "save_history": bool(save_history)}
    # create the file readable by the current user only, since it holds the API key
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as outfile:
        json.dump(settings, outfile, indent=2)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
