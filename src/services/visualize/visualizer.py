from services.llm_client import LLMClient
from prompts.prompt_manager import PromptManager
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Visualizer(LLMClient):
    """Base Visualizer class using LLMClient."""
    def __init__(self, model="gpt-4.1", temperature=0.0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)
        self.prompt_manager = PromptManager()

    def visualize(self, summary: str, mode="visualization") -> str:
        prompt = self.prompt_manager.get(mode).format(summary=summary)
        output = self.run(prompt)
        return self.extract_html(output)

    def extract_html(self, html: str) -> str:
        pattern = r"```html(.*?)```"
        match = re.search(pattern, html, re.DOTALL)
        if match:
            html_content = match.group(1).strip()
            html_content = html_content.replace("html", "").strip()
            html_content = html_content.replace("`", "").strip()
            logger.info("HTML visualization extracted successfully.")
            return html_content
        else:
            logger.warning("No HTML content found in the provided string.")
            return ""