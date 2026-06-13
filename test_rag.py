from rag_answer import ask_jira

question = "IMEI number is not storing in POS Database "

result = ask_jira(question)

print(result)