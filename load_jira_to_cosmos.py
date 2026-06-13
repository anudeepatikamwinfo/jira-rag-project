import pandas as pd
import re
from azure.cosmos import CosmosClient, PartitionKey

# ==================================================
# COSMOS DB EMULATOR SETTINGS
# ==================================================

ENDPOINT = "https://localhost:8081/"
KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

# ==================================================
# CONNECT TO COSMOS DB
# ==================================================

client = CosmosClient(
    ENDPOINT,
    credential=KEY,
    connection_verify=False
)

database = client.create_database_if_not_exists(
    id="JiraKnowledgeBase"
)

container = database.create_container_if_not_exists(
    id="JiraTickets",
    partition_key=PartitionKey(path="/ticketNumber")
)

print("Connected to Cosmos DB")

# ==================================================
# READ EXCEL
# ==================================================

file_path = r"data\jira-rag-project.xlsx"

df = pd.read_excel(file_path)

print(f"Total Tickets Found: {len(df)}")

# Uncomment for testing only
# df = df.head(10)

df = df.fillna("")

print("Loading Jira tickets into Cosmos DB...")

loaded_count = 0
failed_count = 0

# ==================================================
# PROCESS EACH ROW
# ==================================================

for _, row in df.iterrows():

    try:

        # ------------------------------------------
        # Jira Issue Key
        # ------------------------------------------

        raw_ticket_number = str(row.get("Issue key", "")).strip()

        if not raw_ticket_number:
            continue

        ticket_number = re.sub(
            r'[^\w\-]',
            '_',
            raw_ticket_number
        )

        # ------------------------------------------
        # Jira Internal Issue ID
        # ------------------------------------------

        jira_issue_id = str(
            row.get("Issue id", "")
        ).strip()

        if not jira_issue_id:
            continue

        # ------------------------------------------
        # Main Fields
        # ------------------------------------------

        summary = str(row.get("Summary", ""))
        description = str(row.get("Description", ""))

        issue_type = str(row.get("Issue Type", ""))
        status = str(row.get("Status", ""))
        priority = str(row.get("Priority", ""))

        assignee = str(row.get("Assignee", ""))
        reporter = str(row.get("Reporter", ""))

        resolution = str(row.get("Resolution", ""))

        created = str(row.get("Created", ""))
        updated = str(row.get("Updated", ""))

        parent_key = str(row.get("Parent key", ""))
        parent_summary = str(row.get("Parent summary", ""))

        labels = str(row.get("Labels", ""))

        # ------------------------------------------
        # Collect All Comment Columns
        # ------------------------------------------

        comments = ""

        for col in df.columns:

            if "Comment" in str(col):

                value = str(
                    row.get(col, "")
                ).strip()

                if value:
                    comments += value + "\n"

        # ------------------------------------------
        # Build Searchable Content
        # ------------------------------------------

        content = f"""
Issue Key:
{ticket_number}

Summary:
{summary}

Description:
{description}

Comments:
{comments}

Resolution:
{resolution}

Parent Summary:
{parent_summary}

Status:
{status}

Priority:
{priority}

Issue Type:
{issue_type}
"""

        # ------------------------------------------
        # Cosmos Document
        # ------------------------------------------

        document = {
            "id": jira_issue_id,
            "ticketNumber": ticket_number,

            "summary": summary,
            "description": description,
            "comments": comments,

            "status": status,
            "priority": priority,
            "issueType": issue_type,

            "assignee": assignee,
            "reporter": reporter,

            "resolution": resolution,

            "created": created,
            "updated": updated,

            "parentKey": parent_key,
            "parentSummary": parent_summary,

            "labels": labels,

            # Future Vector Embedding Source
            "content": content
        }

        container.upsert_item(document)

        loaded_count += 1

        if loaded_count % 100 == 0:
            print(f"{loaded_count} tickets loaded...")

    except Exception as ex:

        failed_count += 1

        print(f"\nFailed Ticket: {raw_ticket_number}")
        print(f"Error: {str(ex)}")

# ==================================================
# COMPLETED
# ==================================================

print("\n====================================")
print("LOAD COMPLETED")
print("====================================")

print(f"Loaded Tickets : {loaded_count}")
print(f"Failed Tickets : {failed_count}")