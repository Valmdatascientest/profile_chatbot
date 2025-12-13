import os
import requests

class LLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    def __init__(self, model: str = None, base_url: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate(self, prompt: str) -> str:
        r = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["response"].strip()

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()

def get_llm_provider() -> LLMProvider:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        return OpenAIProvider(api_key=api_key)
    return OllamaProvider()