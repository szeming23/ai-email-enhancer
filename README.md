# AI email enhancer

Python tkinter UI that allows layman to leverage on AI (OpenAI GPT models) to enhance their emails with proper grammar as well as more creative adjectives and better structure.

## how to run

``pip install -r requirements.txt``

``python main.py``

Click **Settings** to enter your OpenAI API key and choose the model (the window opens automatically on first run). You can also edit the prompt given to the model there, and turn on saving of prompts and responses to a history file. Settings are saved to `~/.ai-email-enhancer/settings.json`, outside the project folder, and are re-read on every request, so changes apply immediately. If no key is saved, the `OPENAI_API_KEY` environment variable is used.

Pick a **Tone** next to the Enhance button to make the email formal, friendly, concise, etc.

## how to build a standalone app with PyInstaller (Windows `.exe`, macOS `.app`, Linux binary)

PyInstaller builds for the operating system it is run on, so run this on the system you want the app for:

``pip install pyinstaller``

``pyinstaller --onefile --windowed --name ai-email-enhancer main.py``

The app is created in the `dist` folder. `--windowed` stops a console window from opening alongside the app.

## how to convert a `.py` to `.app` file (for macOS)

Either run the PyInstaller command above on a Mac (it creates `dist/ai-email-enhancer.app`), or use py2app:

``pip3 install py2app``

``py2applet --make-setup main.py``

``rm -rf build dist``

Build in alias mode:  
``python3 setup.py py2app -A``

Build for deployment, if working properly in alias mode:  
``python3 setup.py py2app``
