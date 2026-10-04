import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from enhancer import enhance_email, list_models, TONES
from settings import load_settings, save_settings, DEFAULT_MODEL, DEFAULT_PROMPT, SETTINGS_PATH
from history import HISTORY_PATH

SUGGESTED_MODELS = [DEFAULT_MODEL, "gpt-4o", "gpt-4.1-mini", "gpt-4.1"]

# responses from the background thread, picked up by check_response on the UI thread
responses = queue.Queue()

def run_model(body, tone):
    try:
        response = enhance_email(body, tone)
    except Exception as e:
        response = f"Error encountered:\n{e}"
    responses.put(response)

def enhance():
    # get input
    input_text = text_input.get("1.0", "end").strip()
    if not input_text:
        return
    # call the model in a background thread so the window does not freeze
    button_enhance.config(state=tk.DISABLED, text="Working...")
    threading.Thread(target=run_model, args=(input_text, tone_var.get()), daemon=True).start()
    root.after(100, check_response)

def check_response():
    try:
        response = responses.get_nowait()
    except queue.Empty:
        root.after(100, check_response)
        return
    # replace text_output with response
    text_output.delete("1.0", "end")
    text_output.insert(tk.INSERT, response)
    button_enhance.config(state=tk.NORMAL, text="Enhance")

def update_title():
    root.title(f"AI email enhancer ({load_settings()['model']})")

def open_settings():
    settings = load_settings()
    window = tk.Toplevel(root)
    window.title("Settings")
    window.resizable(False, False)
    window.transient(root)
    window.grab_set()

    api_key_var = tk.StringVar(value=settings["api_key"])
    model_var = tk.StringVar(value=settings["model"])
    show_key_var = tk.BooleanVar(value=False)
    save_history_var = tk.BooleanVar(value=settings["save_history"])

    ## API key
    tk.Label(window, text="API key").grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 3))
    entry_key = tk.Entry(window, textvariable=api_key_var, width=50, show="*")
    entry_key.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=(0, 10), pady=(10, 3))
    def toggle_key():
        entry_key.config(show="" if show_key_var.get() else "*")
    tk.Checkbutton(window, text="Show key", variable=show_key_var,
                   command=toggle_key).grid(row=1, column=1, sticky=tk.W)

    ## model (can pick from the list or type any model name)
    tk.Label(window, text="Model").grid(row=2, column=0, sticky=tk.W, padx=10, pady=3)
    combo_model = ttk.Combobox(window, textvariable=model_var, values=SUGGESTED_MODELS, width=35)
    combo_model.grid(row=2, column=1, sticky=tk.EW, pady=3)
    def refresh_models():
        # ask the API which models this key can use
        try:
            models = list_models(api_key_var.get().strip())
        except Exception as e:
            messagebox.showerror("Settings", f"Could not fetch models:\n{e}", parent=window)
            return
        if models:
            combo_model.config(values=models)
    tk.Button(window, text="Refresh list", command=refresh_models).grid(row=2, column=2, padx=(5, 10), pady=3)

    ## prompt (the instruction given to the model, the tone is added to it)
    tk.Label(window, text="Prompt").grid(row=3, column=0, sticky=tk.NW, padx=10, pady=3)
    text_prompt = tk.Text(window, width=50, height=5, wrap=tk.WORD)
    text_prompt.grid(row=3, column=1, columnspan=2, sticky=tk.EW, padx=(0, 10), pady=3)
    text_prompt.insert("1.0", settings["prompt"])
    def reset_prompt():
        text_prompt.delete("1.0", "end")
        text_prompt.insert("1.0", DEFAULT_PROMPT)
    tk.Button(window, text="Reset prompt", command=reset_prompt).grid(row=4, column=1, sticky=tk.W)

    ## history
    tk.Checkbutton(window, text="Save prompts and responses to history", variable=save_history_var).grid(
        row=5, column=1, columnspan=2, sticky=tk.W, pady=(8, 0))
    tk.Label(window, text=HISTORY_PATH, fg="gray").grid(row=6, column=1, columnspan=2, sticky=tk.W)

    tk.Label(window, text=f"Settings are saved to {SETTINGS_PATH}", fg="gray").grid(
        row=7, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(10, 3))

    ## save / cancel buttons
    def save():
        if not model_var.get().strip():
            messagebox.showerror("Settings", "Model cannot be empty.", parent=window)
            return
        try:
            save_settings(api_key_var.get(), model_var.get(),
                          text_prompt.get("1.0", "end"), save_history_var.get())
        except OSError as e:
            messagebox.showerror("Settings", f"Could not save settings:\n{e}", parent=window)
            return
        update_title()
        window.destroy()
    wrapper_buttons = tk.Frame(window)
    wrapper_buttons.grid(row=8, column=0, columnspan=3, sticky=tk.E, padx=10, pady=10)
    tk.Button(wrapper_buttons, text="Cancel", padx=3, pady=3, command=window.destroy).pack(side=tk.RIGHT, padx=(5, 0))
    tk.Button(wrapper_buttons, text="Save", padx=3, pady=3, command=save).pack(side=tk.RIGHT)

    entry_key.focus_set()

root = tk.Tk()
## main structure
### wrapper 1: input email
wrapper1 = tk.LabelFrame(root, text="Input email here", padx=5, pady=3)
wrapper1.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
### tone, enhance and settings:
wrapper_buttons = tk.Frame(root)
wrapper_buttons.pack(expand=False, pady=3)
tk.Label(wrapper_buttons, text="Tone").pack(side=tk.LEFT, padx=3)
tone_var = tk.StringVar(value=list(TONES)[0])
combo_tone = ttk.Combobox(wrapper_buttons, textvariable=tone_var, values=list(TONES),
                          state="readonly", width=18)
combo_tone.pack(side=tk.LEFT, padx=3)
button_enhance = tk.Button(wrapper_buttons, text="Enhance", padx=3, pady=3, width=10, command=enhance)
button_enhance.pack(side=tk.LEFT, padx=3)
button_settings = tk.Button(wrapper_buttons, text="Settings", padx=3, pady=3, command=open_settings)
button_settings.pack(side=tk.LEFT, padx=3)
### wrapper 2: model output
wrapper2 = tk.LabelFrame(root, text="Enhanced email", padx=5, pady=3)
wrapper2.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

## input email box (small requested size, so the boxes share whatever space the window has)
text_input = ScrolledText(wrapper1, wrap=tk.WORD, height=5, width=40)
text_input.pack(fill=tk.BOTH, expand=True)

## output email box
text_output = ScrolledText(wrapper2, wrap=tk.WORD, height=5, width=40)
text_output.pack(fill=tk.BOTH, expand=True)


root.geometry('750x600') # width x height
root.minsize(450, 350)
update_title()
# first run: no key saved yet, so open the settings window straight away
if not load_settings()["api_key"]:
    root.after(100, open_settings)
root.mainloop()
