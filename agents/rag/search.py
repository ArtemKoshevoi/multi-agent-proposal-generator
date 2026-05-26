import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "developer_profiles"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)


def search_profile(query: str, developer_id: str, n_results: int = 5) -> list[str]:
    """Searches the given developer's profile for content relevant to the query."""
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"developer_id": developer_id},
    )
    return (results["documents"] or [[]])[0]
