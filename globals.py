from langchain_ollama import ChatOllama
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv

load_dotenv()

# TODO: model selector on landing
model = ChatOllama(model="llama3.1:8b", temperature=0)
serper = GoogleSerperAPIWrapper()
current_project: str = ""
