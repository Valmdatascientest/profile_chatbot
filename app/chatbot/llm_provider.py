from __future__ import annotations

import requests
from app.config import settings


class LLMProvider:
    def generate(self, system: str, user: str, temperature: float = 0.2) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self):
        from openai import OpenAI  # import lazy
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, system: str, user: str, temperature: float = 0.2) -> str:
        resp = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def generate(self, system: str, user: str, temperature: float = 0.2) -> str:
        r = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        return (data.get("message", {}) or {}).get("content", "").strip()


def get_llm_provider() -> LLMProvider:
    if settings.openai_api_key:
        return OpenAIProvider()
    return OllamaProvider()