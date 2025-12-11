"""
app/api/main.py

API FastAPI pour le chatbot de profil.

- Charge l'index (vector_store.pkl) construit par app.indexing.build_index
- Expose une route /chat pour répondre aux questions des recruteurs
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.indexing.embedder import Embedder
from app.indexing.vector_store import SimpleVectorStore
from app.chatbot.qa_pipeline import CareerChatbot

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config globale
# ---------------------------------------------------------------------------

# Chemin par défaut vers le vector store (tu peux changer via env/config si tu veux)
DEFAULT_VECTOR_STORE_PATH = Path("data/processed/vector_store.pkl")

app = FastAPI(
    title="Career Chatbot API",
    description="Chatbot personnel basé sur CV + LinkedIn pour répondre aux recruteurs.",
    version="0.1.0",
)

# CORS (pratique si tu appelles depuis Streamlit ou une autre UI front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre pour la prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Objets globaux (initialisés au startup)
embedder: Embedder | None = None
vector_store: SimpleVectorStore | None = None
chatbot: CareerChatbot | None = None


# ---------------------------------------------------------------------------
# Modèles Pydantic
# ---------------------------------------------------------------------------

class Question(BaseModel):
    query: str


class Answer(BaseModel):
    answer: str


class HealthStatus(BaseModel):
    status: str
    has_vector_store: bool
    has_embedder: bool
    has_chatbot: bool


# ---------------------------------------------------------------------------
# Fonctions internes
# ---------------------------------------------------------------------------

def _load_vector_store(path: Path) -> SimpleVectorStore:
    if not path.exists():
        raise RuntimeError(
            f"Vector store introuvable à {path}. "
            f"Tu dois d'abord construire l'index avec : "
            f'python -m app.indexing.build_index --cv-path data/raw/cv.pdf --linkedin-dir data/raw'
        )

    logger.info("Chargement du vector store depuis %s", path)
    with path.open("rb") as f:
        obj = pickle.load(f)

    if not isinstance(obj, SimpleVectorStore):
        raise TypeError(
            f"Le fichier {path} ne contient pas un SimpleVectorStore. "
            "Vérifie que l'index a été construit avec la bonne version du code."
        )

    logger.info(
        "Vector store chargé avec %d chunks.",
        len(obj.chunks),
    )
    return obj


# ---------------------------------------------------------------------------
# Évènements FastAPI
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    """
    Initialisation du chatbot au démarrage de l'API.
    """
    global embedder, vector_store, chatbot

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    logger.info("=== Démarrage de l'API Career Chatbot ===")
    logger.info("Modèle d'embeddings : %s", settings.embedding_model)
    logger.info("Modèle LLM : %s", settings.llm_model)

    # 1. Chargement du vector store
    try:
        vector_store = _load_vector_store(DEFAULT_VECTOR_STORE_PATH)
    except Exception as e:  # pragma: no cover - log
        logger.exception("Erreur lors du chargement du vector store: %s", e)
        raise

    # 2. Initialisation de l'embedder
    try:
        embedder = Embedder(model_name=settings.embedding_model)
        logger.info("Embedder initialisé.")
    except Exception as e:  # pragma: no cover - log
        logger.exception("Erreur lors de l'initialisation de l'embedder: %s", e)
        raise

    # 3. Initialisation du chatbot
    try:
        chatbot = CareerChatbot(vector_store=vector_store, embedder=embedder)
        logger.info("Chatbot initialisé et prêt à répondre ✅")
    except Exception as e:  # pragma: no cover - log
        logger.exception("Erreur lors de l'initialisation du chatbot: %s", e)
        raise


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    """
    Endpoint de santé simple pour vérifier que tout est bien chargé.
    """
    return HealthStatus(
        status="ok",
        has_vector_store=vector_store is not None,
        has_embedder=embedder is not None,
        has_chatbot=chatbot is not None,
    )


@app.post("/chat", response_model=Answer)
async def chat(question: Question) -> Answer:
    """
    Pose une question au chatbot de profil.

    Exemple de payload:
    {
        "query": "Quelles sont tes compétences principales en Python et data ?"
    }
    """
    if chatbot is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot non initialisé. Vérifie que l'API a démarré correctement.",
        )

    if not question.query.strip():
        raise HTTPException(
            status_code=400,
            detail="La question ne peut pas être vide.",
        )

    try:
        answer_text = chatbot.answer(question.query)
    except Exception as e:  # pragma: no cover - log
        logger.exception("Erreur lors de la génération de réponse: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la génération de la réponse.",
        ) from e

    return Answer(answer=answer_text)