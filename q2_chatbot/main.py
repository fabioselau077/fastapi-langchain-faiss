import argparse
import os
import sys

from openai import OpenAIError

from chatbot.chain import PythonChatbot

EXIT_COMMANDS = {"/sair", "sair", "exit", "quit"}
RESET_COMMAND = "/limpar"

DEMO_QUESTIONS = [
    "Como criar uma lista em Python?",
    "E como eu removo um item dela?",  # só faz sentido com o histórico
    "Qual a diferença entre lista e tupla?",
    "Qual a capital da França?",  # fora do objetivo o bot deve (ou deveria) recusar
]


def print_answer(bot: PythonChatbot, question: str) -> None:
    for chunk in bot.stream(question):
        print(chunk, end="", flush=True)
    print("\n")


def run_demo(bot: PythonChatbot) -> None:
    for question in DEMO_QUESTIONS:
        print(f"Você: {question}\n")
        print("Bot: ", end="")
        print_answer(bot, question)
        print("-" * 60 + "\n")


def run_chat(bot: PythonChatbot) -> None:
    print("Chatbot de Python. Pode perguntar!")
    print(f"Comandos: {RESET_COMMAND} limpa o histórico, /sair encerra.\n")

    while True:
        try:
            question = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAté mais!")
            break

        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            print("Até mais!")
            break
        if question.lower() == RESET_COMMAND:
            bot.reset()
            print("Histórico limpo.\n")
            continue

        print("\nBot: ", end="")
        try:
            print_answer(bot, question)
        except OpenAIError as error:
            print(f"\nErro ao consultar a OpenAI: {error}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot de dúvidas sobre Python.")
    parser.add_argument(
        "--demo", action="store_true", help="roda perguntas de exemplo e encerra"
    )
    args = parser.parse_args()

    # o .env já foi carregado antes
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY não configurada. Copie o .env.example para .env e preencha a chave.")

    bot = PythonChatbot()
    if args.demo:
        run_demo(bot)
    else:
        run_chat(bot)


if __name__ == "__main__":
    main()