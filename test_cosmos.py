from azure.cosmos import CosmosClient, PartitionKey


endpoint = "https://localhost:8081/"
key = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

client = CosmosClient(
    endpoint,
    credential=key,
    connection_verify=False
)
database = client.create_database_if_not_exists(
    id="JiraKnowledgeBase"
)

container = database.create_container_if_not_exists(
    id="JiraTickets",
    partition_key=PartitionKey(path="/ticketNumber")
)

print("Database and Container Created Successfully")