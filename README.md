# Profile Career Chatbot

Profile Career Chatbot est un chatbot de type RAG (Retrieval-Augmented Generation) permettant de répondre à des recruteurs à partir d’un CV et d’un profil LinkedIn. Le projet utilise des embeddings locaux et un modèle de langage configurable. Il fonctionne sans aucune API key par défaut grâce à un LLM local via Ollama, tout en restant compatible avec OpenAI de manière optionnelle.

## Fonctionnalités

- Recherche sémantique basée sur un vector store
- Embeddings locaux avec Sentence-Transformers
- LLM local par défaut via Ollama (sans clé)
- Support optionnel d’OpenAI si une clé API est fournie
- Réponses en français, professionnelles, à la première personne
- Réponses basées uniquement sur le contexte fourni (CV et LinkedIn)

## Architecture

app/
├── chatbot/
│   ├── qa_pipeline.py        Pipeline de question-réponse (RAG)
│   └── llm_provider.py       Gestion du LLM (OpenAI ou Ollama)
├── indexing/
│   ├── embedder.py           Embeddings locaux
│   └── vector_store.py       Stockage vectoriel
├── config.py                 Configuration centralisée
└── main.py                   Point d’entrée de l’application

## Prérequis

- Python 3.10 ou supérieur
- pip ou poetry
- Un CPU standard suffit (GPU non requis)
- Ollama recommandé pour une utilisation sans API key

## Installation

1. Cloner le dépôt :
   git clone https://github.com/Valmdatascientest/profile_chatbot.git
   cd profile_chatbot

2. Installer les dépendances :
   pip install -r requirements.txt

## Utilisation sans API key (par défaut)

1. Installer Ollama depuis https://ollama.com
2. Télécharger un modèle :
   ollama pull llama3.1:8b
3. Lancer le service Ollama :
   ollama serve
4. Lancer l’application :
   python -m app.main

Le chatbot fonctionne alors entièrement en local, sans dépendance à une API externe.

## Configuration optionnelle

Il est possible de créer un fichier .env à la racine du projet pour personnaliser la configuration :

OPENAI_API_KEY=
LLM_MODEL=gpt-4.1-mini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

## Utilisation avec OpenAI (optionnel)

Pour utiliser OpenAI, renseigner la variable OPENAI_API_KEY dans le fichier .env, puis relancer l’application. Le projet détecte automatiquement la présence de la clé et utilise OpenAI comme modèle de langage.

## Comportement du modèle de langage

- Si OPENAI_API_KEY est définie, OpenAI est utilisé
- Si aucune clé n’est fournie, Ollama local est utilisé
- Les embeddings sont toujours calculés localement


## Améliorations possibles

- Ajout d’une interface utilisateur (Streamlit ou Gradio)
- Remplacement du vector store simple par FAISS
- Ajout d’une mémoire de conversation
- Gestion de plusieurs profils
- Déploiement Docker complet

## Licence

Projet pédagogique libre d’utilisation.