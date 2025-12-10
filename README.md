 Career Chatbot FR

Chatbot personnel en Python permettant aux recruteurs d’interroger votre profil à partir de votre CV + LinkedIn grâce à un pipeline RAG (Retrieval Augmented Generation).

 Fonctionnalités
	•	Extraction automatique du texte du CV (PDF)
	•	Import des données LinkedIn (JSON / CSV)
	•	Vectorisation des informations via embeddings
	•	Base de connaissances personnelle (FAISS / vecteurs)
	•	Chatbot intelligent répondant aux questions des recruteurs
	•	API FastAPI + Interface Streamlit


 Architecture du projet

	career-chatbot-fr/
	├── app/
	│   ├── config.py
	│   ├── ingestion/
	│   │   ├── cv_loader.py
	│   │   ├── linkedin_loader.py
	│   ├── indexing/
	│   │   ├── embedder.py
	│   │   ├── vector_store.py
	│   ├── chatbot/
	│   │   ├── qa_pipeline.py
	│   ├── api/
	│   │   ├── main.py
	│   └── ui/
	│       ├── streamlit_app.py
	├── data/
	│   ├── raw/
	│   └── processed/
	├── tests/
	│   ├── test_ingestion.py
	│   ├── test_indexing.py
	│   └── test_chatbot.py
	├── .env.example
	├── requirements.txt
	└── README.md

	 Installation

	1️⃣ Créer l’environnement Python

	python -m venv venv
	source venv/bin/activate

	2️⃣ Installer les dépendances

	pip install -r requirements.txt

	3️⃣ Copier votre CV

	data/raw/cv.pdf

	4️⃣ Ajouter votre export LinkedIn

	data/raw/LinkedIn_Export.json

	▶️ Lancer l’API

	uvicorn app.api.main:app --reload

	▶️ Lancer l’interface Streamlit

	streamlit run app/ui/streamlit_app.py

	Technologies utilisées
		•	Python 3.10+
		•	FastAPI
		•	Streamlit
		•	SentenceTransformers
		•	FAISS ou stockage vecteurs custom
		•	OpenAI / HuggingFace (au choix)
		•	pdfplumber

	⸻

	 Objectif du projet

	Ce projet a pour but de démontrer :
		•	Compétences Python avancées
		•	Structuration propre d’un projet
		•	API REST moderne
		•	NLP + embeddings + RAG
		•	UI légère
		•	MLOps minimal (tests, env, doc…)

⸻

