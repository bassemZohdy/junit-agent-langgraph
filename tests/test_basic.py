import pytest
import sys
import os
# Import directly from the config.py file
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import settings as pydantic_settings


def test_config_loaded():
    # Check that the base URL is set and has the expected scheme
    assert pydantic_settings.ollama_base_url.startswith("http")
    assert pydantic_settings.ollama_model is not None  # Just check that it's set
