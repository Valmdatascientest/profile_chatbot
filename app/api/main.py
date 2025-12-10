from fastapi import FastAPI
from pydantic import BaseModel

from app.indexing.embedder import Embedder
from app.indexing.vector_store import SimpleVectorStore
from app.chatbot.qa_pipeline import CareerChatbot

app = FastAPI(title="My Profile Chatbot API")

# ==== Init global objects (dans un vrai projet tu chargerais les données depuis disque) ====
embedder = Embedder()
vector_store = SimpleVectorStore()

# TODO: charger le texte du CV et de LinkedIn, faire les chunks, puis:
# texts = [...]
# embeddings = embedder.encode(texts)
# vector_store.add_documents(texts, embeddings)

chatbot = CareerChatbot(vector_store, embedder)


class Question(BaseModel):
    query: str


class Answer(BaseModel):
    answer: str


@app.post("/chat", response_model=Answer)
def chat(question: Question):
    answer = chatbot.answer(question.query)
    return Answer(answer=answer)