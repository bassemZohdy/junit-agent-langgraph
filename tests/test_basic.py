import pytest
from src.config import settings


def test_config_loaded():
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_model == "llama3.2"
