"""
app/ingestion/linkedin_loader.py

Version mise à jour incluant :
- Profile.csv
- Positions.csv
- Education.csv
- Skills.csv
- Certifications.csv
- Projects.csv / Projets.csv

Transforme tout en une base de connaissances textuelle pour le chatbot.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import json
import logging
import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================
#   Dataclasses
# ============================================================

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
class Certification:
    name: str
    authority: Optional[str] = None
    license_number: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class Project:
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class LinkedInData:
    profile: Optional[ProfileSummary]
    positions: List[Position]
    educations: List[Education]
    skills: List[Skill]
    certifications: List[Certification]
    projects: List[Project]


# ============================================================
#   Utilitaires
# ============================================================

def _safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path).fillna("")
    except Exception as e:
        logger.warning("Erreur de lecture CSV %s: %s", path, e)
        return None


# ============================================================
#   Loading des sections LinkedIn
# ============================================================

def load_profile(raw_dir: Path) -> Optional[ProfileSummary]:
    for filename in ["Profile.csv", "profile.csv"]:
        df = _safe_read_csv(raw_dir / filename)
        if df is not None and not df.empty:
            row = df.iloc[0]

            return ProfileSummary(
                first_name=str(row.get("First Name", "")).strip() or None,
                last_name=str(row.get("Last Name", "")).strip() or None,
                headline=str(row.get("Headline", "")).strip() or None,
                summary=str(row.get("Summary", "")).strip() or None,
                location=str(row.get("Location", "")).strip() or None,
            )
    return None


def load_positions(raw_dir: Path) -> List[Position]:
    names = ["Positions.csv", "positions.csv", "Experience.csv", "experience.csv"]

    for filename in names:
        df = _safe_read_csv(raw_dir / filename)
        if df is None:
            continue

        positions = []
        for _, row in df.iterrows():
            title = row.get("Title", "")
            company = row.get("Company Name", "") or row.get("Company", "")

            if not (title or company):
                continue

            positions.append(
                Position(
                    title=str(title).strip(),
                    company=str(company).strip(),
                    location=str(row.get("Location", "")).strip() or None,
                    description=str(row.get("Description", "")).strip() or None,
                    start_date=str(row.get("Started On", "")).strip() or None,
                    end_date=str(row.get("Finished On", "")).strip() or None,
                )
            )

        return positions

    return []


def load_educations(raw_dir: Path) -> List[Education]:
    for filename in ["Education.csv", "education.csv"]:
        df = _safe_read_csv(raw_dir / filename)
        if df is None:
            continue

        educations = []
        for _, row in df.iterrows():
            school = row.get("School Name", "") or row.get("School", "")
            if not school:
                continue

            educations.append(
                Education(
                    school=str(school).strip(),
                    degree=str(row.get("Degree Name", "")).strip() or None,
                    field_of_study=str(row.get("Field Of Study", "")).strip() or None,
                    start_date=str(row.get("Started On", "")).strip() or None,
                    end_date=str(row.get("Finished On", "")).strip() or None,
                )
            )
        return educations

    return []


def load_skills(raw_dir: Path) -> List[Skill]:
    for filename in ["Skills.csv", "skills.csv"]:
        df = _safe_read_csv(raw_dir / filename)
        if df is None:
            continue

        return [Skill(name=str(row.get("Name", "")).strip())
                for _, row in df.iterrows()
                if row.get("Name", "").strip()]

    return []


def load_certifications(raw_dir: Path) -> List[Certification]:
    for filename in ["Certifications.csv", "certifications.csv"]:
        df = _safe_read_csv(raw_dir / filename)
        if df is None:
            continue

        certs = []
        for _, row in df.iterrows():
            name = row.get("Name", "") or row.get("Certification Name", "")
            if not name:
                continue

            certs.append(
                Certification(
                    name=str(name).strip(),
                    authority=str(row.get("Authority", "")).strip() or None,
                    license_number=str(row.get("License Number", "")).strip() or None,
                    start_date=str(row.get("Started On", "")).strip() or None,
                    end_date=str(row.get("Finished On", "")).strip() or None,
                )
            )
        return certs

    return []


def load_projects(raw_dir: Path) -> List[Project]:
    names = ["Projects.csv", "projects.csv", "Projets.csv", "projets.csv"]

    for filename in names:
        df = _safe_read_csv(raw_dir / filename)
        if df is None:
            continue

        projects = []
        for _, row in df.iterrows():
            title = row.get("Title", "") or row.get("Project", "")
            if not title:
                continue

            projects.append(
                Project(
                    title=str(title).strip(),
                    description=str(row.get("Description", "")).strip() or None,
                    url=str(row.get("URL", "")).strip() or None,
                    start_date=str(row.get("Started On", "")).strip() or None,
                    end_date=str(row.get("Finished On", "")).strip() or None,
                )
            )
        return projects

    return []


# ============================================================
#   Chargement complet
# ============================================================

def load_linkedin_export(raw_dir: str | Path) -> LinkedInData:
    raw_dir = Path(raw_dir)

    profile = load_profile(raw_dir)
    positions = load_positions(raw_dir)
    educations = load_educations(raw_dir)
    skills = load_skills(raw_dir)
    certifications = load_certifications(raw_dir)
    projects = load_projects(raw_dir)

    return LinkedInData(
        profile=profile,
        positions=positions,
        educations=educations,
        skills=skills,
        certifications=certifications,
        projects=projects,
    )


# ============================================================
#   Conversion en chunks textuels
# ============================================================

def linkedin_data_to_text_chunks(data: LinkedInData) -> List[str]:
    chunks: List[str] = []

    # Profil
    if data.profile:
        p = data.profile
        lines = []
        if p.first_name or p.last_name:
            lines.append(f"Nom : {p.first_name or ''} {p.last_name or ''}".strip())
        if p.headline:
            lines.append(f"Titre LinkedIn : {p.headline}")
        if p.location:
            lines.append(f"Localisation : {p.location}")
        if p.summary:
            lines.append(f"Résumé : {p.summary}")
        chunks.append("Profil LinkedIn\n" + "\n".join(lines))

    # Expériences
    for pos in data.positions:
        chunk = (
            "Expérience professionnelle\n"
            f"Poste : {pos.title}\n"
            f"Entreprise : {pos.company}\n"
        )
        if pos.location:
            chunk += f"Localisation : {pos.location}\n"
        if pos.start_date or pos.end_date:
            chunk += f"Période : {pos.start_date or '?'} → {pos.end_date or 'Présent'}\n"
        if pos.description:
            chunk += f"Description : {pos.description}"
        chunks.append(chunk)

    # Formations
    for edu in data.educations:
        chunk = (
            "Formation\n"
            f"Établissement : {edu.school}\n"
        )
        if edu.degree:
            chunk += f"Diplôme : {edu.degree}\n"
        if edu.field_of_study:
            chunk += f"Domaine d'étude : {edu.field_of_study}\n"
        if edu.start_date or edu.end_date:
            chunk += f"Période : {edu.start_date or '?'} → {edu.end_date or '?'}"
        chunks.append(chunk)

    # Compétences
    if data.skills:
        skills_text = ", ".join(s.name for s in data.skills)
        chunks.append("Compétences LinkedIn : " + skills_text)

    # Certifications
    for cert in data.certifications:
        chunk = f"Certification : {cert.name}\n"
        if cert.authority:
            chunk += f"Authority : {cert.authority}\n"
        if cert.license_number:
            chunk += f"Licence : {cert.license_number}\n"
        if cert.start_date or cert.end_date:
            chunk += f"Période : {cert.start_date or '?'} → {cert.end_date or '?'}"
        chunks.append(chunk)

    # Projets
    for proj in data.projects:
        chunk = f"Projet : {proj.title}\n"
        if proj.description:
            chunk += f"Description : {proj.description}\n"
        if proj.url:
            chunk += f"URL : {proj.url}\n"
        if proj.start_date or proj.end_date:
            chunk += f"Période : {proj.start_date or '?'} → {proj.end_date or '?'}"
        chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raw_dir = Path("data/raw")
    data = load_linkedin_export(raw_dir)
    chunks = linkedin_data_to_text_chun