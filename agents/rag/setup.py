from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

DEVELOPERS_PATH = "mock_data/developers"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "developer_profiles"


def setup_vector_db():
    """Loads all developer profiles into ChromaDB. Run once before using the system."""

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()

    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    total_chunks = 0
    for profile_path in sorted(Path(DEVELOPERS_PATH).glob("*.txt")):
        developer_id = profile_path.stem  # e.g. "artem_koshevoi"

        loader = TextLoader(str(profile_path), encoding="utf-8")
        documents = loader.load()
        chunks = splitter.split_documents(documents)

        collection.add(
            documents=[chunk.page_content for chunk in chunks],
            ids=[f"{developer_id}_chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"developer_id": developer_id} for _ in chunks],
        )

        print(f"  {developer_id}: {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\nVector DB ready: {total_chunks} total chunks in '{COLLECTION_NAME}'")
    return collection


if __name__ == "__main__":
    setup_vector_db()
