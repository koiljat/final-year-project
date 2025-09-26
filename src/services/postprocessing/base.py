from ..llm_client import LLMClient
from ...prompts.prompt_manager import PromptManager
import logging

logger = logging.getLogger(__name__)

class BasePostProcessor(LLMClient):
    """Base class for post-processing operations like Simplify, Shorten, Rephrase."""

    def __init__(self, model=None, temperature=0.0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)
        self.prompt_manager = PromptManager()

    def process(self, text: str) -> str:
        """Override in subclasses to implement specific operations"""
        raise NotImplementedError("Subclasses must implement `process` method.")
