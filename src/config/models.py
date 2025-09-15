"""
Data models and configuration classes for the Streamlit Summarization App.
These dataclasses provide type safety and structure for data passed between components.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class SummarizationMethod(Enum):
    """Enumeration of available summarization methods."""
    DEFAULT = "Default"
    RAG = "RAG" 
    MAP_REDUCE = "MapReduce"


class PostProcessingAction(Enum):
    """Enumeration of post-processing actions."""
    SIMPLIFY = "Simplify"
    SHORTEN = "Shorten"
    EXPAND = "Expand"
    REPHRASE = "Rephrase"


class Provider(Enum):
    """Enumeration of AI model providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"


# Model name to provider mapping
MODEL_PROVIDER_MAPPING = {
    "gpt-5": Provider.OPENAI,
    "gpt-4.1": Provider.OPENAI,
    "gpt-4o": Provider.OPENAI,
    "gpt-4": Provider.OPENAI,
    "o4-mini": Provider.OPENAI,
    "gemini-2.5-flash": Provider.GEMINI,
    "sonar": Provider.PERPLEXITY,
}

AVAILABLE_MODELS = [
    "gpt-5",
    "gpt-4.1",
    "gpt-4o",
    "gpt-4",
    "o4-mini",
    "gemini-2.5-flash",
    "sonar",
]

# Default model
DEFAULT_MODEL = "gpt-4o"

DEFAULT_MODEL_SETTINGS = {
    "temperature": 0.0,
    "max_tokens": 3500,
    "top_p": 0.05,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}


# Method configuration with descriptions and icons
SUMMARIZATION_METHODS = {
    SummarizationMethod.DEFAULT: {
        "description": "Quick and efficient summarization",
        "icon": "⚡",
        "recommended_for": "General documents under 5000 words"
    },
    SummarizationMethod.RAG: {
        "description": "Retrieval-augmented generation for enhanced context",
        "icon": "🧠",
        "recommended_for": "Complex documents requiring deep understanding"
    },
    SummarizationMethod.MAP_REDUCE: {
        "description": "Hierarchical summarization for long documents",
        "icon": "🗂️",
        "recommended_for": "Very long documents (10,000+ words)"
    },
}


# Default session state values
DEFAULT_SESSION_STATE = {
    "summarize_input": "",
    "current_result": None,
    "processed_result": None,
    "result_ls": None,
    "processing_time": None,
    "original_word_count": 0,
    "summary_word_count": 0,
    "file_uploaded": False,
    "processing_status": None,
}


def get_provider_for_model(model_name: str) -> Provider:
    """
    Get the provider for a given model name.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Provider enum value
    """
    return MODEL_PROVIDER_MAPPING.get(model_name, Provider.OPENAI)