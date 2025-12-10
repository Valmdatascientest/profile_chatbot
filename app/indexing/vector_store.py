from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class DocumentChunk:
    id: int
    text: str
    embedding: np.ndarray


class SimpleVectorStore:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []

    def add_documents(self, texts: List[str], embeddings: np.ndarray):
        for i, (text, emb) in enumerate(zip(texts, embeddings)):
            self.chunks.append(
                DocumentChunk(id=len(self.chunks) + i, text=text, embedding=emb)
            )

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        scores = []
        for chunk in self.chunks:
            score = self._cosine_similarity(query_embedding, chunk.embedding)
            scores.append((chunk, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]