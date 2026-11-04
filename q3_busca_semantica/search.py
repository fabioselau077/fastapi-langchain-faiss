import argparse
import sys

from semantic_search.embeddings import Embedder
from semantic_search.store import INDEX_DIR, SearchResult, VectorStore

# nenhuma consulta repete as palavras do post esperado
# a ideia é mostrar que a busca entende o assunto, não o texto
DEMO_QUERIES = [
    "quero gastar menos no fim do mês",
    "não consigo pegar no sono à noite",
    "como lidar com falhas no meu código",
    "decoração verde para casa pequena",
    "rodar minha aplicação em qualquer servidor",
    "fazer comida no forno em casa",
]


def print_results(query: str, results: list[SearchResult]) -> None:
    print(f"\nConsulta: {query}")
    for position, result in enumerate(results, start=1):
        print(f"  {position}. [{result.score:.2f}] {result.document.title}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca semântica nos posts do blog.")
    parser.add_argument("query", nargs="?", help="texto da consulta")
    parser.add_argument("-k", type=int, default=3, help="quantidade de resultados (padrão: 3)")
    parser.add_argument("--demo", action="store_true", help="roda consultas de exemplo")
    args = parser.parse_args()

    if not args.query and not args.demo:
        parser.error("informe uma consulta ou use --demo")

    if not (INDEX_DIR / "index.faiss").exists():
        sys.exit("Índice não encontrado. Rode antes: python build_index.py")

    store = VectorStore.load(Embedder())
    queries = DEMO_QUERIES if args.demo else [args.query]

    for query in queries:
        print_results(query, store.search(query, k=args.k))


if __name__ == "__main__":
    main()