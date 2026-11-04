import pytest

# --- EBOOK VÁLIDO PARA TESTE ---
VALID_BOOK = {
    "title": "Dom Casmurro",
    "author": "Machado de Assis",
    "published_date": "1899-01-01",
    "summary": "Bentinho narra sua vida e o ciúme que sente de Capitu.",
}


# --- Cadastro ---

def test_create_book_returns_201_with_id(client):
    response = client.post("/books", json=VALID_BOOK)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == VALID_BOOK["title"]
    assert data["published_date"] == VALID_BOOK["published_date"]


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", ""),
        ("title", "   "),
        ("author", ""),
        ("summary", ""),
        ("published_date", "2024-13-45"),
        ("published_date", "ontem"),
    ],
)
def test_create_book_rejects_invalid_fields(client, field, value):
    payload = {**VALID_BOOK, field: value}
    response = client.post("/books", json=payload)

    assert response.status_code == 422


def test_create_book_rejects_missing_field(client):
    payload = {k: v for k, v in VALID_BOOK.items() if k != "author"}
    response = client.post("/books", json=payload)

    assert response.status_code == 422


# --- Consulta ---

def test_search_by_title_is_partial_and_case_insensitive(client, sample_books):
    response = client.get("/books", params={"title": "CASMURRO"})

    assert response.status_code == 200
    titles = [b["title"] for b in response.json()]
    assert titles == ["Dom Casmurro"]


def test_search_by_author(client, sample_books):
    response = client.get("/books", params={"author": "machado"})

    titles = [b["title"] for b in response.json()]
    assert titles == ["Dom Casmurro", "Memórias Póstumas de Brás Cubas"]


def test_search_combining_title_and_author(client, sample_books):
    response = client.get("/books", params={"title": "dom", "author": "machado"})

    titles = [b["title"] for b in response.json()]
    assert titles == ["Dom Casmurro"]


def test_search_without_filters_lists_all(client, sample_books):
    response = client.get("/books")

    assert len(response.json()) == len(sample_books)


def test_search_without_match_returns_empty_list(client, sample_books):
    response = client.get("/books", params={"title": "Harry Potter"})

    assert response.status_code == 200
    assert response.json() == []


def test_search_treats_percent_as_literal(client, sample_books):
    # sem o autoescape, "%" casaria com qualquer título
    response = client.get("/books", params={"title": "%"})

    assert response.json() == []


def test_search_respects_limit(client, sample_books):
    response = client.get("/books", params={"limit": 2})

    assert len(response.json()) == 2


# --- Detalhe ---

def test_get_book_by_id(client):
    created = client.post("/books", json=VALID_BOOK).json()
    response = client.get(f"/books/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_book_not_found(client):
    response = client.get("/books/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Livro não encontrado"