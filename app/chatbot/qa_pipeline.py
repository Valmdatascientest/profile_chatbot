"""
app/chatbot/qa_pipeline.py

Pipeline de QA pour le chatbot de profil
- OpenAI si OPENAI_API_KEY est défini
- Sinon fallback local via Ollama (sans clé)
"""

from __future__ import annotations

from typing import List

from app.config import settings
from app.chatbot.llm_provider import get_llm_provider
from app.indexing.embedder import Embedder
from app.indexing.vector_store import SimpleVectorStore


class CareerChatbot:
    def __init__(self, vector_store: SimpleVectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder
        self.llm = get_llm_provider()

    def build_context(self, query: str, top_k: int = 5) -> List[str]:
        query_emb = self.embedder.encode([query])[0]
        results = self.vector_store.search(query_emb, top_k=top_k)
        return [chunk.text for chunk, _ in results]

    def answer(self, query: str) -> str:
        context_chunks = self.build_context(query)
        context = "\n\n".join(context_chunks)

        prompt = f"""
Tu es un assistant qui répond aux recruteurs à partir des informations ci-dessous.

Contexte (CV + LinkedIn) :
{context}

Question du recruteur :
{query}

Réponds en français, de manière professionnelle, à la première personne ("je"),
en t'appuyant uniquement sur les informations du contexte.
Si une information ne se trouve pas dans le contexte, indique-le clairement.
""".strip()

        system = "Tu es un assistant spécialisé dans les profils candidats."

        return self.llm.generate(system=system, user=prompt, temperature=0.2)