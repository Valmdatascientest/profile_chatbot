"""
app/chatbot/qa_pipeline.py

Pipeline de QA pour le chatbot de profil, compatible avec openai>=1.0.0
"""

from __future__ import annotations

from typing import List

from openai import OpenAI

from app.config import settings
from app.indexing.embedder import Embedder
from app.indexing.vector_store import SimpleVectorStore


class CareerChatbot:
    def __init__(self, vector_store: SimpleVectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY non défini. Renseigne ta clé dans l'environnement ou le fichier .env."
            )

        # Nouveau client OpenAI (openai>=1.0.0)
        self.client = OpenAI(api_key=settings.openai_api_key)

    def build_context(self, query: str, top_k: int = 5) -> List[str]:
        """
        Encode la question, recherche les top_k passages pertinents
        dans le vector store, et renvoie leurs textes.
        """
        query_emb = self.embedder.encode([query])[0]
        results = self.vector_store.search(query_emb, top_k=top_k)
        return [chunk.text for chunk, _ in results]

    def answer(self, query: str) -> str:
        """
        Génère une réponse en utilisant le contexte (CV + LinkedIn)
        et un LLM OpenAI (modèle défini dans settings.llm_model).
        """
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
"""

        response = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "Tu es un assistant spécialisé dans les profils candidats."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()