from typing import List
import openai  # ou openai>=1.x selon la lib que tu utilises

from app.config import settings
from app.indexing.embedder import Embedder
from app.indexing.vector_store import SimpleVectorStore


class CareerChatbot:
    def __init__(self, vector_store: SimpleVectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key

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

Réponds en français, en restant factuel, professionnel, et à la première personne ("je").
Si l'information n'est pas dans le contexte, dis-le honnêtement.
"""

        # Exemple pour l'API openai "chat completions" (à adapter à la version de la lib)
        response = openai.ChatCompletion.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response["choices"][0]["message"]["content"].strip()