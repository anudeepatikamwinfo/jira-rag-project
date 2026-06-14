import re
import requests
from vector_search import search


def get_section(text, section):

    pattern = rf"{section}:\s*(.*?)(?=\n\n[A-Z][A-Za-z ]*:|\Z)"

    match = re.search(
        pattern,
        text,
        re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return "Not Available"


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
            "issueSummary": "No relevant Jira tickets found.",
            "rootCause": "Not Available",
            "fixImplemented": "Not Available",
            "workaround": "Not Available",
            "relevantTickets": []
        }

    context = build_context(tickets)

    prompt = f"""
You are a senior Jira support analyst.

Analyze the Jira tickets and answer in EXACTLY this format.

Issue Summary:
<summary>

Root Cause:
<root cause>

Fix Implemented:
<fix implemented>

Relevant Jira Tickets:
<ticket numbers>

Workaround:
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

    print("\n========== RAW RESPONSE ==========")
    print(answer)
    print("==================================")

    issue_summary = get_section(
        answer,
        "Issue Summary"
    )

    root_cause = get_section(
        answer,
        "Root Cause"
    )

    fix_implemented = get_section(
        answer,
        "Fix Implemented"
    )

    workaround = get_section(
        answer,
        "Workaround"
    )

    relevant_tickets_text = get_section(
        answer,
        "Relevant Jira Tickets"
    )

    relevant_tickets = []

    for ticket in tickets:

        if ticket["ticketNumber"] in relevant_tickets_text:

            relevant_tickets.append({
                "ticketNumber": ticket["ticketNumber"],
                "summary": ticket["summary"],
                "score": ticket["score"]
            })

    # Fallback if model does not mention tickets
    if not relevant_tickets:

        relevant_tickets = [
            {
                "ticketNumber": t["ticketNumber"],
                "summary": t["summary"],
                "score": t["score"]
            }
            for t in tickets
        ]

    return {
        "issueSummary": issue_summary,
        "rootCause": root_cause,
        "fixImplemented": fix_implemented,
        "workaround": workaround,
        "relevantTickets": relevant_tickets
    }