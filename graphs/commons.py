from langchain.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper

serper = GoogleSerperAPIWrapper()


@tool
def search_internet(query: str) -> str:
    """
    Search the internet for any query and receive a string response.
    """
    return serper.run(query)
