from services.llm_client import LLMClient
from prompts.prompt_manager import PromptManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Visualizer(LLMClient):
    """Base Visualizer class using LLMClient."""
    def __init__(self, model=None, temperature=0.3, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)
        self.prompt_manager = PromptManager()

    def visualize(self, text: str, mode="visualization") -> str:
        prompt = self.prompt_manager.get(mode).format(summary=text)
        return self.run(prompt)