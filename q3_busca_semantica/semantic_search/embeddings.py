import numpy as np
from sentence_transformers import SentenceTransformer

# escolhi um modelo multilíngue porque os posts estão em português, modelos treinados em inglês vai perder qualidade
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class Embedder:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        # com os vetores normalizados, o produto interno calculado pelo
        # FAISS é igual à similaridade de cosseno
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(vectors, dtype="float32")