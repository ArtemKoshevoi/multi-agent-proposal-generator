import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "developer_profile"


def get_collection():
    """Returns the ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )


def search_profile(query: str, n_results: int = 3) -> list[str]:
    """Searches developer profile for content relevant to the query."""
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results["documents"][0]


if __name__ == "__main__":
    # test with a few different queries
    queries = [
        "React e-commerce experience",
        "long-term contract reliability",
        "trading platform real-time data",
    ]

    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        results = search_profile(query)
        for i, result in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(result[:300])