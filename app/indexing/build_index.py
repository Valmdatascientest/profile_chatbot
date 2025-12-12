"""
app/indexing/build_index.py

Script pour construire l'index (base de connaissances vectorielle)
à partir du CV et de l'export LinkedIn.

Usage (depuis la racine du projet) :

    python -m app.indexing.build_index \
        --cv-path data/raw/cv.pdf \
        --linkedin-dir data/raw \
        --output-dir data/processed
"""

from __future__ import annotations

import argparse
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

from app.ingestion.cv_loader import load_cv_document, cv_to_text_chunks
from app.ingestion.linkedin_loader import (
    load_linkedin_export,
    linkedin_data_to_text_chunks,
)
from app.indexing.embedder import Embedder
from app.indexing.vector_store import SimpleVectorStore

logger = logging.getLogger(__name__)


def build_knowledge_base(
    cv_path: Path,
    linkedin_dir: Path,
) -> Dict[str, Any]:
    """
    Construit la base de connaissances à partir du CV + LinkedIn.

    Retourne un dict avec :
        - "texts": List[str] (tous les chunks)
        - "embeddings": np.ndarray
    """
    # =======================
    # CV
    # =======================
    logger.info("Chargement du CV : %s", cv_path)
    cv_doc = load_cv_document(cv_path)
    cv_chunks = cv_to_text_chunks(cv_doc)
    logger.info("Chunks CV générés : %d", len(cv_chunks))

    # =======================
    # LinkedIn
    # =======================
    logger.info("Chargement de l'export LinkedIn depuis : %s", linkedin_dir)
    linkedin_data = load_linkedin_export(linkedin_dir)

    # Logs détaillés sur ce qui a été trouvé
    if linkedin_data.profile:
        logger.info("Profil LinkedIn détecté.")
    else:
        logger.info("Aucun profil LinkedIn détecté.")

    logger.info("Positions LinkedIn : %d", len(linkedin_data.positions))
    logger.info("Formations LinkedIn : %d", len(linkedin_data.educations))
    logger.info("Compétences LinkedIn : %d", len(linkedin_data.skills))
    logger.info("Certifications LinkedIn : %d", len(linkedin_data.certifications))
    logger.info("Projets LinkedIn : %d", len(linkedin_data.projects))

    linkedin_chunks = linkedin_data_to_text_chunks(linkedin_data)
    logger.info("Chunks LinkedIn générés (profil + expériences + formations + compétences + certifications + projets) : %d", len(linkedin_chunks))

    # =======================
    # Fusion
    # =======================
    all_texts: List[str] = cv_chunks + linkedin_chunks
    logger.info("Nombre total de chunks (CV + LinkedIn) : %d", len(all_texts))

    if not all_texts:
        raise RuntimeError(
            "Aucun texte à indexer. Vérifiez que le CV et l'export LinkedIn sont bien présents."
        )

    # =======================
    # Embeddings
    # =======================
    logger.info("Initialisation de l'embedder...")
    embedder = Embedder()
    logger.info("Génération des embeddings...")
    embeddings = embedder.encode(all_texts)
    logger.info("Embeddings générés : shape %s", embeddings.shape)

    return {
        "texts": all_texts,
        "embeddings": embeddings,
    }


def save_index(
    knowledge_base: Dict[str, Any],
    output_dir: Path,
) -> None:
    """
    Sauvegarde la base de connaissances et un vector store pré-construit.

    - data/processed/knowledge_base.pkl
    - data/processed/vector_store.pkl
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    kb_path = output_dir / "knowledge_base.pkl"
    vs_path = output_dir / "vector_store.pkl"

    texts: List[str] = knowledge_base["texts"]
    embeddings: np.ndarray = knowledge_base["embeddings"]

    logger.info("Création du vector store en mémoire...")
    vector_store = SimpleVectorStore()
    vector_store.add_documents(texts, embeddings)
    logger.info("Vector store créé avec %d documents.", len(vector_store.chunks))

    logger.info("Sauvegarde de la knowledge base : %s", kb_path)
    with kb_path.open("wb") as f:
        pickle.dump(
            {
                "texts": texts,
                "embeddings": embeddings,
            },
            f,
        )

    logger.info("Sauvegarde du vector store : %s", vs_path)
    with vs_path.open("wb") as f:
        pickle.dump(vector_store, f)

    logger.info("Index sauvegardé avec succès.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Construire l'index (CV + LinkedIn) pour le chatbot de profil."
    )
    parser.add_argument(
        "--cv-path",
        type=str,
        default="data/raw/cv.pdf",
        help="Chemin vers le fichier CV (pdf/docx).",
    )
    parser.add_argument(
        "--linkedin-dir",
        type=str,
        default="data/raw",
        help="Dossier contenant les fichiers exportés de LinkedIn.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed",
        help="Dossier de sortie pour les fichiers d'index.",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    args = parse_args()

    cv_path = Path(args.cv_path)
    linkedin_dir = Path(args.linkedin_dir)
    output_dir = Path(args.output_dir)

    logger.info("=== Construction de l'index ===")
    logger.info("CV: %s", cv_path)
    logger.info("LinkedIn dir: %s", linkedin_dir)
    logger.info("Output dir: %s", output_dir)

    kb = build_knowledge_base(cv_path=cv_path, linkedin_dir=linkedin_dir)
    save_index(kb, output_dir=output_dir)

    logger.info("=== Index construit avec succès ✅ ===")


if __name__ == "__main__":
    main()