import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda

from chatbot.chain import PythonChatbot


def test_ask_returns_model_answer(make_bot):
    bot = make_bot(["Use colchetes: minha_lista = [1, 2, 3]"])

    answer = bot.ask("Como criar uma lista em Python?")

    assert answer == "Use colchetes: minha_lista = [1, 2, 3]"


def test_ask_stores_question_and_answer_in_history(make_bot):
    bot = make_bot(["Use colchetes."])

    bot.ask("Como criar uma lista?")

    assert bot.history == [
        HumanMessage("Como criar uma lista?"),
        AIMessage("Use colchetes."),
    ]


def test_system_prompt_is_sent_first(recording_bot):
    bot, calls = recording_bot

    bot.ask("Como criar uma lista?")

    first_message = calls[0][0]
    assert isinstance(first_message, SystemMessage)
    assert "Python" in first_message.content


def test_history_is_sent_on_next_question(recording_bot):
    bot, calls = recording_bot

    bot.ask("Como criar uma lista?")
    bot.ask("E como removo um item dela?")

    # sistema + pergunta anterior + resposta anterior + pergunta nova
    contents = [m.content for m in calls[1][1:]]
    assert contents == [
        "Como criar uma lista?",
        "resposta 1",
        "E como removo um item dela?",
    ]


def test_history_keeps_only_recent_messages(make_bot):
    bot = make_bot(["r1", "r2", "r3"], max_history=4)

    bot.ask("pergunta 1")
    bot.ask("pergunta 2")
    bot.ask("pergunta 3")

    assert [m.content for m in bot.history] == ["pergunta 2", "r2", "pergunta 3", "r3"]


def test_stream_yields_full_answer_and_updates_history(make_bot):
    bot = make_bot(["Listas usam colchetes."])

    chunks = list(bot.stream("Como criar uma lista?"))

    assert len(chunks) > 1
    assert "".join(chunks) == "Listas usam colchetes."
    assert bot.history[-1] == AIMessage("Listas usam colchetes.")


def test_failed_answer_is_not_saved_in_history():
    def broken_llm(_):
        raise RuntimeError("API fora do ar")

    bot = PythonChatbot(llm=RunnableLambda(broken_llm))

    with pytest.raises(RuntimeError):
        list(bot.stream("Como criar uma lista?"))

    assert bot.history == []


def test_reset_clears_history(make_bot):
    bot = make_bot(["Use colchetes."])
    bot.ask("Como criar uma lista?")

    bot.reset()

    assert bot.history == []