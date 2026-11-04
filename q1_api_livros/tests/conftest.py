import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Reaproveita a mesma conexão no banco, se não tá limite de pool no futuro
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_books(client):
    books = [
        {
            "title": "Dom Casmurro",
            "author": "Machado de Assis",
            "published_date": "1899-01-01",
            "summary": "Bentinho narra sua vida e o ciúme que sente de Capitu.",
        },
        {
            "title": "Memórias Póstumas de Brás Cubas",
            "author": "Machado de Assis",
            "published_date": "1881-01-01",
            "summary": "Um defunto autor conta a própria vida.",
        },
        {
            "title": "O Cortiço",
            "author": "Aluísio Azevedo",
            "published_date": "1890-01-01",
            "summary": "A vida em um cortiço no Rio de Janeiro do século XIX.",
        },
        {
            "title": "Vidas Secas",
            "author": "Graciliano Ramos",
            "published_date": "1938-01-01",
            "summary": "Uma família de retirantes foge da seca no sertão.",
        },
    ]
    for book in books:
        client.post("/books", json=book)
    return books