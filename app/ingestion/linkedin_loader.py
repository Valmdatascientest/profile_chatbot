"""
app/ingestion/linkedin_loader.py

Module pour charger et transformer un export LinkedIn
en texte structuré utilisable par le chatbot de profil.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)


# =========================
#   Modèles de données
# =========================

@dataclass
class ProfileSummary:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Position:
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class Education:
    school: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class Skill:
    name: str


@dataclass
class LinkedInData:
    profile: Optional[ProfileSummary]
    positions: List[Position]
    educations: List[Education]
    skills: List[Skill]


# =========================
#   Fonctions utilitaires
# =========================

def _safe_read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        logger.info("Fichier JSON non trouvé: %s", path)
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:  # pragma: no cover - log only
        logger.warning("Erreur de lecture JSON %s: %s", path, e)
        return None


def _safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        logger.info("Fichier CSV non trouvé: %s", path)
        return None
    try:
        return pd.read_csv(path)
    except Exception as e:  # pragma: no cover - log only
        logger.warning("Erreur de lecture CSV %s: %s", path, e)
        return None


# =========================
#   Chargement brut
# =========================

def load_profile(raw_dir: str | Path) -> Optional[ProfileSummary]:
    """
    Charge les infos de profil depuis un export LinkedIn.

    On cherche typiquement un fichier "Profile.json"
    (nom exact pouvant varier selon la langue / version).
    """
    raw_dir = Path(raw_dir)

    # Essais de plusieurs noms possibles
    candidate_files = [
        "Profile.json",
        "profile.json",
        "Profile.txt.json",
    ]

    profile_data: Optional[Dict[str, Any]] = None
    for name in candidate_files:
        profile_data = _safe_read_json(raw_dir / name)
        if profile_data:
            break

    if not profile_data:
        return None

    # Les clés exactes peuvent varier, on essaye d'être robustes
    first_name = profile_data.get("firstName") or profile_data.get("First Name")
    last_name = profile_data.get("lastName") or profile_data.get("Last Name")
    headline = profile_data.get("headline") or profile_data.get("Headline")
    summary = profile_data.get("summary") or profile_data.get("Summary")
    location = (
        profile_data.get("locationName")
        or profile_data.get("Location")
        or profile_data.get("location")
    )

    return ProfileSummary(
        first_name=first_name,
        last_name=last_name,
        headline=headline,
        summary=summary,
        location=location,
    )


def load_positions(raw_dir: str | Path) -> List[Position]:
    """
    Charge les expériences professionnelles depuis un export LinkedIn.

    On cherche typiquement un fichier CSV "Positions.csv" ou "Experience.csv".
    """
    raw_dir = Path(raw_dir)

    candidate_files = [
        "Positions.csv",
        "positions.csv",
        "Experience.csv",
        "experience.csv",
    ]

    df: Optional[pd.DataFrame] = None
    for name in candidate_files:
        df = _safe_read_csv(raw_dir / name)
        if df is not None:
            break

    if df is None:
        return []

    df = df.fillna("")

    positions: List[Position] = []
    for _, row in df.iterrows():
        # Noms de colonnes possibles selon l’export
        title = row.get("Title", "") or row.get("title", "")
        company = (
            row.get("Company Name", "")
            or row.get("Company", "")
            or row.get("companyName", "")
        )
        location = row.get("Location", "") or row.get("location", "")
        description = (
            row.get("Description", "")
            or row.get("description", "")
            or row.get("Summary", "")
        )

        start_date = (
            row.get("Started On", "")
            or row.get("Start Date", "")
            or row.get("startDate", "")
        )
        end_date = (
            row.get("Finished On", "")
            or row.get("End Date", "")
            or row.get("endDate", "")
        )

        if not title and not company:
            continue

        positions.append(
            Position(
                title=str(title).strip(),
                company=str(company).strip(),
                location=str(location).strip() or None,
                description=str(description).strip() or None,
                start_date=str(start_date).strip() or None,
                end_date=str(end_date).strip() or None,
            )
        )

    return positions


def load_educations(raw_dir: str | Path) -> List[Education]:
    """
    Charge le parcours scolaire depuis un export LinkedIn.

    On cherche typiquement un fichier CSV "Education.csv".
    """
    raw_dir = Path(raw_dir)

    candidate_files = [
        "Education.csv",
        "education.csv",
    ]

    df: Optional[pd.DataFrame] = None
    for name in candidate_files:
        df = _safe_read_csv(raw_dir / name)
        if df is not None:
            break

    if df is None:
        return []

    df = df.fillna("")

    educations: List[Education] = []
    for _, row in df.iterrows():
        school = (
            row.get("School Name", "")
            or row.get("School", "")
            or row.get("schoolName", "")
        )
        if not school:
            continue

        degree = row.get("Degree Name", "") or row.get("Degree", "")
        field = (
            row.get("Field Of Study", "")
            or row.get("Field of Study", "")
            or row.get("fieldOfStudy", "")
        )

        start_date = (
            row.get("Started On", "")
            or row.get("Start Date", "")
            or row.get("startDate", "")
        )
        end_date = (
            row.get("Finished On", "")
            or row.get("End Date", "")
            or row.get("endDate", "")
        )

        educations.append(
            Education(
                school=str(school).strip(),
                degree=str(degree).strip() or None,
                field_of_study=str(field).strip() or None,
                start_date=str(start_date).strip() or None,
                end_date=str(end_date).strip() or None,
            )
        )

    return educations


def load_skills(raw_dir: str | Path) -> List[Skill]:
    """
    Charge les compétences depuis un export LinkedIn.

    On cherche typiquement un fichier CSV "Skills.csv".
    """
    raw_dir = Path(raw_dir)

    candidate_files = [
        "Skills.csv",
        "skills.csv",
    ]

    df: Optional[pd.DataFrame] = None
    for name in candidate_files:
        df = _safe_read_csv(raw_dir / name)
        if df is not None:
            break

    if df is None:
        return []

    df = df.fillna("")

    skills: List[Skill] = []
    for _, row in df.iterrows():
        name = row.get("Name", "") or row.get("Skill", "") or row.get("name", "")
        if not name:
            continue
        skills.append(Skill(name=str(name).strip()))

    return skills


# =========================
#   Chargement global
# =========================

def load_linkedin_export(raw_dir: str | Path) -> LinkedInData:
    """
    Charge l'ensemble des données LinkedIn utiles au chatbot.

    :param raw_dir: Dossier où se trouvent les fichiers exportés LinkedIn.
                    Ex: "data/raw/linkedin/"
    """
    raw_dir = Path(raw_dir)

    profile = load_profile(raw_dir)
    positions = load_positions(raw_dir)
    educations = load_educations(raw_dir)
    skills = load_skills(raw_dir)

    return LinkedInData(
        profile=profile,
        positions=positions,
        educations=educations,
        skills=skills,
    )


# =========================
#   Conversion en texte
# =========================

def linkedin_data_to_text_chunks(data: LinkedInData) -> List[str]:
    """
    Transforme LinkedInData en liste de chunks de texte
    utilisables pour les embeddings et la recherche sémantique.
    """
    chunks: List[str] = []

    # Profil
    if data.profile:
        p = data.profile
        profil_lines = []
        if p.first_name or p.last_name:
            profil_lines.append(
                f"Nom : {p.first_name or ''} {p.last_name or ''}".strip()
            )
        if p.headline:
            profil_lines.append(f"Titre LinkedIn : {p.headline}")
        if p.location:
            profil_lines.append(f"Localisation : {p.location}")
        if p.summary:
            profil_lines.append(f"Résumé : {p.summary}")

        if profil_lines:
            chunks.append("Profil LinkedIn\n" + "\n".join(profil_lines))

    # Expériences
    for pos in data.positions:
        lines = [
            f"Expérience professionnelle",
            f"Poste : {pos.title}",
            f"Entreprise : {pos.company}",
        ]
        if pos.location:
            lines.append(f"Localisation : {pos.location}")
        if pos.start_date or pos.end_date:
            lines.append(f"Période : {pos.start_date or '?'} → {pos.end_date or 'Présent'}")
        if pos.description:
            lines.append(f"Description : {pos.description}")

        chunks.append("\n".join(lines))

    # Éducation
    for edu in data.educations:
        lines = [
            "Formation",
            f"Établissement : {edu.school}",
        ]
        if edu.degree:
            lines.append(f"Diplôme : {edu.degree}")
        if edu.field_of_study:
            lines.append(f"Domaine d'étude : {edu.field_of_study}")
        if edu.start_date or edu.end_date:
            lines.append(f"Période : {edu.start_date or '?'} → {edu.end_date or '?'}")

        chunks.append("\n".join(lines))

    # Compétences
    if data.skills:
        skill_names = [s.name for s in data.skills]
        skills_text = "Compétences LinkedIn : " + ", ".join(skill_names)
        chunks.append(skills_text)

    return chunks


if __name__ == "__main__":
    # Petit test manuel possible :
    # python -m app.ingestion.linkedin_loader
    logging.basicConfig(level=logging.INFO)
    example_dir = Path("data/raw")
    li_data = load_linkedin_export(example_dir)
    text_chunks = linkedin_data_to_text_chunks(li_data)
    print(f"{len(text_chunks)} chunks générés depuis LinkedIn.")
    for c in text_chunks[:3]:
        print("----")
        print(c)