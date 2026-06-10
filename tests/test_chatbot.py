import unittest
import sys
import types
from unittest.mock import Mock, patch

# Le test mocke l'appel HTTP, donc il n'a pas besoin du vrai package requests.
sys.modules.setdefault("requests", types.SimpleNamespace(post=None))
sys.modules.setdefault(
    "app.config",
    types.SimpleNamespace(
        settings=types.SimpleNamespace(
            ollama_base_url="http://localhost:11434",
            ollama_model="llama3.1:8b",
            openai_api_key=None,
            llm_model="gpt-4.1-mini",
        )
    ),
)

from app.chatbot.llm_provider import OllamaProvider


class LLMProviderTests(unittest.TestCase):
    @patch("app.chatbot.llm_provider.requests.post")
    def test_ollama_provider_formats_request_and_returns_content(self, mock_post: Mock) -> None:
        response = Mock()
        response.json.return_value = {"message": {"content": "Réponse générée"}}
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        provider = OllamaProvider()
        answer = provider.generate(
            system="Tu réponds aux recruteurs.",
            user="Quelles sont tes compétences ?",
            temperature=0.1,
        )

        self.assertEqual(answer, "Réponse générée")
        mock_post.assert_called_once()
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["stream"], False)
        self.assertEqual(payload["options"]["temperature"], 0.1)
