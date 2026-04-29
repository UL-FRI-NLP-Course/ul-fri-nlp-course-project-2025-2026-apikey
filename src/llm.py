import requests
from src.config import OLLAMA_MODEL, OLLAMA_URL


def ask_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"Error contacting Ollama: {exc}"

    try:
        data = response.json()
    except ValueError:
        return "Error: Ollama returned an invalid response."

    if "response" not in data:
        return "Error: Ollama response did not include generated text."

    return str(data["response"])