import os

os.environ["LANGSMITH_TRACING"] = "false"

import pytest  # noqa: E402
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402
from langchain_core.runnables import RunnableLambda  # noqa: E402

from chatbot.chain import PythonChatbot  # noqa: E402


@pytest.fixture
def make_bot():
    def _make(responses: list[str], max_history: int = 10) -> PythonChatbot:
        return PythonChatbot(
            llm=FakeListChatModel(responses=responses), max_history=max_history
        )

    return _make


@pytest.fixture
def recording_bot():
    """Bot cujo modelo guarda as mensagens recebidas em cada chamada."""
    calls = []

    def fake_llm(prompt_value):
        calls.append(prompt_value.to_messages())
        return AIMessage(content=f"resposta {len(calls)}")

    bot = PythonChatbot(llm=RunnableLambda(fake_llm))
    return bot, calls