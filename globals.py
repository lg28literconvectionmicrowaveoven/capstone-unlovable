from langchain_ollama import ChatOllama

sigint: bool = False
# TODO: model selector on landing
model = ChatOllama(model="llama3.1:8b", temperature=0)
current_project: str = ""
