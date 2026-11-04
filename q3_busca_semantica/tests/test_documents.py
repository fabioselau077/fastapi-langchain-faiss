from semantic_search.documents import load_documents


def test_load_documents_reads_all_posts():
    documents = load_documents()

    assert len(documents) == 12
    assert len({doc.id for doc in documents}) == 12


def test_document_text_includes_title_and_content():
    doc = load_documents()[0]

    assert doc.title in doc.text
    assert doc.content in doc.text