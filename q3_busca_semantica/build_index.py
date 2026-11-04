from semantic_search.documents import load_documents
from semantic_search.embeddings import Embedder
from semantic_search.store import INDEX_DIR, VectorStore


def main() -> None:
    documents = load_documents()

    store = VectorStore(Embedder())
    store.add_documents(documents)
    store.save()

    print(f"{len(documents)} documentos indexados em {INDEX_DIR}")


if __name__ == "__main__":
    main()