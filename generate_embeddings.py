from sentence_transformers import SentenceTransformer

from azure.cosmos import CosmosClient

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Model loaded successfully")

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

documents = list(
    container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True
    )
)

print(f"Found {len(documents)} documents")

for doc in documents:

    content = doc.get("content", "")

    if not content:
        continue

    embedding = model.encode(
        content
    ).tolist()

    doc["embedding"] = embedding

    container.upsert_item(doc)

    print(
        f"Updated {doc['ticketNumber']}"
    )

    