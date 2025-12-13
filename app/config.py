# app/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI (OPTIONNEL)
    openai_api_key: str | None = None
    llm_model: str = "gpt-4.1-mini"

    # Ollama (par défaut si pas de clé OpenAI)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Embeddings (local)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"


settings = Settings()