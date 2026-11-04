import os

from dotenv import load_dotenv

# procura o .env subindo as pastas, então acha o da raiz do projeto
load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# limita o histórico enviado ao modelo pra conversa longa não estourar o contexto nem o custo
MAX_HISTORY_MESSAGES = 10