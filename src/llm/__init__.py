from langchain_ollama import ChatOllama
from ..config import settings


def create_llm():
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=settings.ollama_temperature,
        num_predict=settings.ollama_max_tokens,
    )
