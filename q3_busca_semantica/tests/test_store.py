import pytest

from tests.conftest import FakeEmbedder
from semantic_search.documents import load_documents
from semantic_search.store import VectorStore


def test_search_returns_most_similar_first(store):
    results = store.search("carros elétricos")

    assert results[0].document.id == 2


def test_scores_are_in_descending_order(store):
    scores = [r.score for r in store.search("gatos e café", k=3)]

    assert scores == sorted(scores, reverse=True)


def test_search_respects_k(store):
    assert len(store.search("gatos", k=2)) == 2


def test_k_larger_than_index_returns_all_documents(store, documents):
    assert len(store.search("gatos", k=10)) == len(documents)


def test_identical_text_has_score_close_to_one(store, documents):
    # confirma que os vetores estão normalizados (cosseno = 1)
    result = store.search(documents[2].text, k=1)[0]

    assert result.document.id == 3
    assert result.score == pytest.approx(1.0, abs=1e-5)


@pytest.mark.parametrize("query", ["", "   "])
def test_empty_query_raises_error(store, query):
    with pytest.raises(ValueError):
        store.search(query)


def test_invalid_k_raises_error(store):
    with pytest.raises(ValueError):
        store.search("gatos", k=0)


def test_search_on_empty_store_returns_empty_list():
    assert VectorStore(FakeEmbedder()).search("gatos") == []


def test_documents_added_in_batches_keep_their_positions(documents):
    store = VectorStore(FakeEmbedder())
    store.add_documents(documents[:2])
    store.add_documents(documents[2:])

    assert store.search("café forte", k=1)[0].document.id == 3


def test_save_and_load_return_same_results(store, tmp_path):
    store.save(tmp_path)
    loaded = VectorStore.load(FakeEmbedder(), tmp_path)

    original = store.search("gatos dormem")
    reloaded = loaded.search("gatos dormem")

    assert [r.document for r in reloaded] == [r.document for r in original]
    assert [r.score for r in reloaded] == pytest.approx([r.score for r in original])


@pytest.mark.integration
def test_real_model_finds_post_without_shared_words():
    # importado aqui para não carregar o torch nos testes rápidos
    from semantic_search.embeddings import Embedder

    store = VectorStore(Embedder())
    store.add_documents(load_documents())

    result = store.search("quero viajar barato", k=1)[0]

    assert result.document.title == "Mochilão pela América do Sul gastando pouco"