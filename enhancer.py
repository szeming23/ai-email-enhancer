from openai import OpenAI
from settings import load_settings
from history import save_to_history

# tone name shown in the UI -> extra instruction added to the prompt
TONES = {
    "Keep original tone": "",
    "Formal": "Use a formal, professional tone.",
    "Friendly": "Use a warm, friendly tone.",
    "Concise": "Make it as concise as possible without losing any information.",
    "Persuasive": "Use a confident, persuasive tone.",
    "Apologetic": "Use a polite, apologetic tone.",
}

def get_client(api_key:str):
    if not api_key:
        raise ValueError("No API key set. Click 'Settings' to add your OpenAI API key.")
    return OpenAI(api_key=api_key)

def list_models(api_key:str):
    '''Returns the ids of the chat models available to the given API key.'''
    models = get_client(api_key).models.list()
    return sorted(m.id for m in models if m.id.startswith(("gpt-", "o1", "o3", "o4", "chatgpt-")))

def enhance_email(body:str, tone:str=""):
    '''
    Inputs:
        body: the email
        tone: one of the keys of TONES
    Output:
        model response (the improved email)
    '''
    # settings are read on every call, so changes made in the Settings window apply immediately
    settings = load_settings()
    client = get_client(settings["api_key"])
    prompt = " ".join(filter(None, [settings["prompt"], TONES.get(tone, "")]))
    # Run the model
    response = client.chat.completions.create(
        model=settings["model"],
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": body},
        ],
    )
    clean_response = response.choices[0].message.content or ""
    if settings["save_history"]:
        save_to_history(settings["model"], prompt, body, clean_response)
    return clean_response
