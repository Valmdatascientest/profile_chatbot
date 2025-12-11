# Career Chatbot FR

Ce projet fournit un chatbot permettant de répondre aux questions d’un recruteur à partir de votre CV et de votre export LinkedIn.  
Il utilise un pipeline RAG (Retrieval Augmented Generation) basé sur des embeddings et une recherche sémantique.

---

## Objectif du projet

- Centraliser les données professionnelles d’un candidat (CV + LinkedIn).
- Construire une base de connaissances vectorisée permettant des réponses contextualisées.
- Fournir une API FastAPI pour interroger le chatbot.
- Proposer une interface utilisateur simple via Streamlit.
- Permettre un déploiement léger via Docker et Docker Compose.

---

## Fonctionnalités

- Extraction du texte d’un CV (PDF ou DOCX).
- Import des données exportées depuis LinkedIn.
- Découpage automatique du CV en sections.
- Génération de chunks textuels optimisés pour les embeddings.
- Création d’un index vectoriel (SimpleVectorStore).
- API REST `/chat` pour poser une question.
- Interface Streamlit pour une utilisation interactive.
- Déploiement via Docker ou Docker Compose.

---

## Architecture du projet

```
career-chatbot-fr/
├── app/
│   ├── config.py
│   ├── ingestion/
│   │   ├── cv_loader.py
│   │   ├── linkedin_loader.py
│   ├── indexing/
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   ├── build_index.py
│   ├── chatbot/
│   │   ├── qa_pipeline.py
│   ├── api/
│   │   ├── main.py
│   └── ui/
│       ├── streamlit_app.py
├── data/
│   ├── raw/
│   │   ├── cv.pdf
│   │   ├── LinkedIn export files...
│   └── processed/
│       ├── vector_store.pkl
│       ├── knowledge_base.pkl
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Prérequis

- Python 3.10+
- pip ou pipenv/poetry
- Docker et Docker Compose (optionnel mais fortement recommandé)
- Une clé API OpenAI

---

# Installation locale (sans Docker)

## 1. Créer l’environnement Python

```
python -m venv venv
source venv/bin/activate
```

## 2. Installer les dépendances

```
pip install -r requirements.txt
```

## 3. Ajouter votre CV et export LinkedIn

Placer votre CV dans :

```
data/raw/cv.pdf
```

Placer vos fichiers LinkedIn exportés dans :

```
data/raw/
```

---

# Génération de l’index (CV + LinkedIn)

Avant de lancer le chatbot, il faut construire l’index vectoriel.

```
python -m app.indexing.build_index \
    --cv-path data/raw/cv.pdf \
    --linkedin-dir data/raw \
    --output-dir data/processed
```

Cela crée :

- `data/processed/knowledge_base.pkl`
- `data/processed/vector_store.pkl`

---

# Lancement de l’API FastAPI

```
uvicorn app.api.main:app --reload
```

API accessible sur :

```
http://localhost:8000
```

Documentation interactive :

```
http://localhost:8000/docs
```

---

# Lancement de l’interface Streamlit

```
streamlit run app/ui/streamlit_app.py
```

Interface accessible sur :

```
http://localhost:8501
```

---

# Déploiement via Docker

## 1. Construire l’image Docker

```
docker build -t career-chatbot-api .
```

## 2. Ajouter un fichier `.env`

Créer un fichier `.env` :

```
OPENAI_API_KEY=your_api_key_here
```

---

# Déploiement via Docker Compose

## 1. Générer l’index

```
docker compose --profile index run --rm indexer
```

Ce service lit vos fichiers dans `data/raw` et écrit l’index dans `data/processed`.

## 2. Lancer l’API et l’UI

```
docker compose up api ui
```

Services accessibles :

- API : http://localhost:8000  
- UI : http://localhost:8501  

---

# FAQ

### Peut-on utiliser un modèle LLM local ?
Oui. Le projet est compatible avec n’importe quel LLM. Il suffit de modifier `qa_pipeline.py`.

### Les données personnelles sont-elles stockées dans l’image Docker ?
Non, elles sont montées en volume via `docker-compose.yml`. Elles ne quittent jamais votre machine.

### Peut-on ajouter une mémoire conversationnelle ?
Oui, il suffit d’ajouter un buffer de messages récents dans la couche chatbot.

---

# Licence

MIT