import re
import zlib

import numpy as np
import pytest

from semantic_search.documents import Document
from semantic_search.store import VectorStore


class FakeEmbedder:
    """Cada palavra soma 1 numa posição do vetor; textos com palavras em comum ficam próximos."""

    def __init__(self, dimension: int = 256):
        self.dimension = dimension

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dimension), dtype="float32")
        for row, text in enumerate(texts):
            for word in re.findall(r"\w+", text.lower()):
                # crc32 em vez de hash(): o hash() do Python muda a cada execução
                vectors[row, zlib.crc32(word.encode()) % self.dimension] += 1

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return vectors / norms


@pytest.fixture
def documents():
    return [
        Document(1, "Gatos", "gatos dormem durante boa parte do dia"),
        Document(2, "Carros", "carros elétricos economizam combustível"),
        Document(3, "Café", "café forte ajuda a acordar pela manhã"),
    ]


@pytest.fixture
def store(documents):
    store = VectorStore(FakeEmbedder())
    store.add_documents(documents)
    return store