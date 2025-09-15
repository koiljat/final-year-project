from services.llm_client import LLMClient
from prompts.prompt_manager import PromptManager
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Quoter(LLMClient):
    """Generate interesting quote from a long context."""

    def __init__(self, model=None, temperature=0.0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)
        self.prompt_manager = PromptManager()

    def quote(self, text: str, mode="quote") -> str:
        # TODO: check the logic
        # go through each paragraph and generate a quote, then return the best one
        best_quote = ""
        for paragraph in text.split("\n\n"):
            prompt = self.prompt_manager.get(mode).format(text=paragraph) # need to update the prompt quote in yaml
            quote = self.run(prompt)
            if quote:
                quotes = quotes if 'quotes' in locals() else []
                quotes.append(quote)
        if quotes:
            judge_prompt = self.prompt_manager.get("judge_quote").format(quotes="\n".join(quotes))
            best_quote = self.run(judge_prompt)
        return best_quote
    
if __name__ == "__main__":
    load_dotenv()
    quoter = Quoter(provider="openai", model="gpt-4o-mini", temperature=0.7)
    text = """In the beginning, there was only darkness. The universe was a vast expanse of nothingness, devoid of light and life. But then, a spark ignited, and from that spark, the first stars were born. These stars shone brightly, illuminating the darkness and bringing warmth to the cold void. As the stars continued to burn, they began to form galaxies, each one a swirling mass of stars, gas, and dust. Within these galaxies, planets began to coalesce, and on at least one of these planets, life took hold. From the simplest single-celled organisms to the most complex forms of life, the universe became a vibrant tapestry of existence. And as life evolved, so too did consciousness, allowing beings to ponder their place in the cosmos and the mysteries of the universe itself."""
    quote = quoter.quote(text)
    print("Generated Quote:")
    print(quote)