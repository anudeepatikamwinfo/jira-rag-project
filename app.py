from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from rag_answer import ask_jira

app = FastAPI(
    title="Jira RAG API",
    version="1.0"
)


class QuestionRequest(BaseModel):
    question: str


class Ticket(BaseModel):
    ticketNumber: str
    score: float
    summary: str


class JiraResponse(BaseModel):
    issueSummary: str
    rootCause: str
    fixImplemented: str
    workaround: str
    relevantTickets: List[Ticket]


@app.post("/ask", response_model=JiraResponse)
def ask(request: QuestionRequest):

    return ask_jira(request.question)