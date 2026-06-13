import numpy as np
from sentence_transformers import SentenceTransformer
from azure.cosmos import CosmosClient

# ==================================================
# LOAD EMBEDDING MODEL
# ==================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded")

# ==================================================
# COSMOS DB CONNECTION
# ==================================================

client = CosmosClient(
    "https://localhost:8081/",
    credential="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
    connection_verify=False
)

database = client.get_database_client(
    "JiraKnowledgeBase"
)

container = database.get_container_client(
    "JiraTickets"
)

# ==================================================
# COSINE SIMILARITY
# ==================================================

def cosine_similarity(v1, v2):

    v1 = np.array(v1)
    v2 = np.array(v2)

    return np.dot(v1, v2) / (
        np.linalg.norm(v1) *
        np.linalg.norm(v2)
    )

# ==================================================
# VECTOR SEARCH
# ==================================================
def search(question, top_k=3):

    print(f"\nSearching for: {question}")

    query_embedding = model.encode(question)

    documents = list(
        container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        )
    )

    print(f"Documents loaded: {len(documents)}")

    results = []

    for doc in documents:

        embedding = doc.get("embedding")

        if embedding is None:
            continue

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        results.append({
    "score": round(float(score), 4),
    "ticketNumber": doc.get("ticketNumber", ""),
    "summary": doc.get("summary", ""),
    "description": doc.get("description", ""),
    "comments": doc.get("comments", ""),
    "resolution": doc.get("resolution", ""),
    "status": doc.get("status", "")
    })

    # Sort by score descending
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Remove duplicate ticket numbers
    unique_results = []
    seen_tickets = set()

    for ticket in results:

        ticket_number = ticket["ticketNumber"]

        if ticket_number in seen_tickets:
            continue

        seen_tickets.add(ticket_number)
        unique_results.append(ticket)

    print(f"Unique tickets found: {len(unique_results)}")

    return unique_results[:top_k]