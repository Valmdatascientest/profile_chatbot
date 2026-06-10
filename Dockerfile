# ============================
#  Image de base
# ============================
FROM python:3.11-slim

# Ne pas bufferiser les logs
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ============================
#  Dépendances système
# ============================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# ============================
#  Dossier de travail
# ============================
WORKDIR /app

# ============================
#  Dépendances Python
# ============================
# On copie seulement requirements.txt pour profiter du cache Docker
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================
#  Code de l'application
# ============================
COPY app app

# Les données personnelles (CV, export LinkedIn, index vectoriel) ne sont pas
# copiées dans l'image. Elles doivent être montées via un volume Docker.

# ============================
#  Port exposé
# ============================
EXPOSE 8000

# ============================
#  Commande par défaut
# ============================
# On lance l'API FastAPI avec uvicorn
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
