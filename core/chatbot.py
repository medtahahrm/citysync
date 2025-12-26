import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # change if you want

def ollama_chat(user_message):
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": user_message,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload)

        if response.status_code != 200:
            return f"❌ Ollama Error: {response.status_code} - {response.text}"

        data = response.json()
        return data.get("response", "❌ No response from Ollama")

    except Exception as e:
        return f"❌ Error: {str(e)}"
