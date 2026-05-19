from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()

# paths relative to project root
PROFILE_PATH = "mock_data/artem_koshevoi.txt"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "developer_profile"


def setup_vector_db():
    """Loads developer profile into ChromaDB. Run once before using the system."""

    # load the txt file
    loader = TextLoader(PROFILE_PATH, encoding="utf-8")
    documents = loader.load()
    print(f"Loaded document: {PROFILE_PATH}")

    # split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"Total chunks: {len(chunks)}")

    # print first 3 chunks so we can verify the split looks correct
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk.page_content[:200])

    # setup ChromaDB with local embedding model
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()

    # delete collection if exists to avoid duplicates on re-run
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"\nDeleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass

    # create collection and add chunks
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )

    collection.add(
        documents=[chunk.page_content for chunk in chunks],
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    print(f"\nVector DB ready: {len(chunks)} chunks in '{COLLECTION_NAME}'")
    return collection


if __name__ == "__main__":
    setup_vector_db()