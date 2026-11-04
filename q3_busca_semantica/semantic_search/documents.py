import json
from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "posts.json"


@dataclass(frozen=True)
class Document:
    id: int
    title: str
    content: str

    @property
    def text(self) -> str:
        # o título vai entrar pq resume o assunto e melhora o embedding
        return f"{self.title}. {self.content}"


def load_documents(path: Path = DATA_PATH) -> list[Document]:
    with path.open(encoding="utf-8") as file:
        return [Document(**item) for item in json.load(file)]