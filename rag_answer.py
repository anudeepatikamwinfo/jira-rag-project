import requests
from vector_search import search


def build_context(tickets):

    context = ""

    for ticket in tickets:

        context += f"""
Similarity Score:
{ticket['score']}

Ticket Number:
{ticket['ticketNumber']}

Summary:
{ticket['summary']}

Description:
{ticket['description']}

Resolution:
{ticket['resolution']}

Comments:
{ticket['comments']}

Status:
{ticket['status']}

--------------------------------------------------
"""

    return context

def ask_jira(question):

    tickets = search(question)

    print("\nTickets Retrieved:")

    for ticket in tickets:
        print(
            ticket["ticketNumber"],
            ticket["score"],
            ticket["summary"]
        )

    if not tickets:
        return {
            "answer": "No relevant Jira tickets found.",
            "tickets": []
        }

    context = build_context(tickets)

    prompt = f"""
You are a senior Jira support analyst.

Analyze the Jira tickets and answer in EXACTLY this format.

Issue Summary
-------------
<summary>

Root Cause
----------
<root cause>

Fix Implemented
---------------
<fix implemented>

Relevant Jira Tickets
---------------------
<ticket numbers>

Workaround
----------
<workaround if available>

Question:
{question}

Jira Tickets:
{context}

Rules:
- Use only information from the provided Jira tickets.
- Include ALL relevant ticket numbers.
- If Root Cause is not explicitly available, infer it from the ticket details.
- If no workaround exists, write 'Not Available'.
- Do not add any extra sections.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False
        }
    )

    answer = response.json()["response"]

    return {
        "answer": answer,
        "ticketCount": len(tickets)
    }