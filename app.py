from fastapi import FastAPI
from pydantic import BaseModel

from rag_answer import ask_jira

app = FastAPI(
    title="Jira RAG API",
    version="1.0"
)

class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():

    return {
        "message": "Jira RAG API Running"
    }


@app.post("/ask")
def ask(request: QuestionRequest):

    result = ask_jira(
        request.question
    )

    return result