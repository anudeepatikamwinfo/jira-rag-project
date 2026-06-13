from vector_search import search

results = search(
    "POS Archive search by Customer ID is not working"
)

print("Total Results:", len(results))

for ticket in results[:10]:

    print()
    print(ticket)