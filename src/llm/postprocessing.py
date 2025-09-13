from llm.llm_client import LLMClient
from prompts.prompt_manager import PromptManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostProcessor(LLMClient):
    """Base PostProcessor class using LLMClient."""
    def __init__(self, model=None, temperature=0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)
        self.prompt_manager = PromptManager()

    def process(self, text: str, mode="default") -> str:
        prompt = self.prompt_manager.get(mode).format(text=text)
        return self.run(prompt)
    
    def split_by_paragraph(self, text: str) -> list[str]:
        """Splits the text into paragraphs."""
        return [para.strip() for para in text.split("\n\n") if para.strip()]