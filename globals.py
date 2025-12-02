from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from threading import Lock

load_dotenv()


class GlobalState:
    _instance: "GlobalState | None" = None
    _instance_lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self._lock = Lock()
        self.current_project: str = ""

        self.model = ChatOllama(model="llama3.1:8b", temperature=0)
        self.serper = GoogleSerperAPIWrapper()


app_state = GlobalState()
