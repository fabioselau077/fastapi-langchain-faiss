from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from . import config

SYSTEM_PROMPT = """Você é um tutor especialista em Python que ajuda pessoas a aprender a linguagem.

Ao responder:
- Explique o conceito de forma clara e didática, em português.
- Mostre exemplos de código curtos e funcionais, em blocos de código.
- Quando houver mais de uma forma de fazer algo, mostre a mais comum primeiro e cite as alternativas.
- Aponte erros comuns relacionados ao assunto quando fizer sentido.

Se a pergunta não for sobre programação em Python, diga educadamente que só pode ajudar com Python."""


def build_llm() -> BaseChatModel:
    return ChatOpenAI(model=config.OPENAI_MODEL, temperature=config.TEMPERATURE)


def build_chain(llm: BaseChatModel):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    return prompt | llm | StrOutputParser()


class PythonChatbot:
    def __init__(
        self,
        llm: BaseChatModel | None = None,
        max_history: int = config.MAX_HISTORY_MESSAGES,
    ):
        # aceitar o modelo por parâmetro permite usar um LLM falso nos testes
        if llm is None:
            llm = build_llm()
        self.chain = build_chain(llm)
        self.max_history = max_history
        self.history: list[BaseMessage] = []

    def ask(self, question: str) -> str:
        answer = self.chain.invoke({"history": self.history, "question": question})
        self._remember(question, answer)
        return answer

    def stream(self, question: str):
        """Devolve a resposta em pedaços, conforme o modelo vai gerando."""
        parts = []
        for chunk in self.chain.stream({"history": self.history, "question": question}):
            parts.append(chunk)
            yield chunk
        self._remember(question, "".join(parts))

    def reset(self) -> None:
        self.history.clear()

    def _remember(self, question: str, answer: str) -> None:
        self.history.extend([HumanMessage(question), AIMessage(answer)])
        # mantém só as mensagens mais recentes; como entram sempre em pares,
        # um limite par preserva pergunta e resposta juntas
        self.history = self.history[-self.max_history:]