import json
from dataclasses import asdict
from pathlib import Path

import faiss

from .documents import Document

INDEX_DIR = Path(__file__).resolve().parent.parent / "index"


class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.index: faiss.Index | None = None
        # a posição de cada documento nesta lista é o id dele dentro do FAISS
        self.documents: list[Document] = []

    def add_documents(self, documents: list[Document]) -> None:
        vectors = self.embedder.encode([doc.text for doc in documents])

        if self.index is None:
            # busca exata; para poucos milhares de documentos é rápida o bastante
            self.index = faiss.IndexFlatIP(vectors.shape[1])

        self.index.add(vectors)
        self.documents.extend(documents)

    def save(self, directory: Path = INDEX_DIR) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(directory / "index.faiss"))
        with (directory / "documents.json").open("w", encoding="utf-8") as file:
            json.dump([asdict(doc) for doc in self.documents], file, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, embedder, directory: Path = INDEX_DIR) -> "VectorStore":
        store = cls(embedder)
        store.index = faiss.read_index(str(directory / "index.faiss"))
        with (directory / "documents.json").open(encoding="utf-8") as file:
            store.documents = [Document(**item) for item in json.load(file)]
        return store