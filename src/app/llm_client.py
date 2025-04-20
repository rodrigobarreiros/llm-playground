import requests

OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'llama3.2'

def query_llm(prompt):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0  # 🧊 garante consistência
            }
        }, timeout=10)

        data = response.json()
        return data.get("response", "Resposta inesperada.")

    except requests.exceptions.Timeout:
        return "Timeout: Ollama demorou demais para responder."
    except requests.exceptions.RequestException as e:
        return f"Erro ao conectar com Ollama: {e}"

