import os
from dotenv import load_dotenv

# LangChain providers
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_perplexity import ChatPerplexity
from langchain_huggingface import ChatHuggingFace
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, provider="perplexity", model=None, temperature=0):
        """
        Initializes the LLM client with the specified provider, model, and temperature.
        Loads environment variables using `load_dotenv()`. Sets up the language model interface
        based on the chosen provider ("openai" or "perplexity"). Raises a ValueError for unknown providers.
        Args:
            provider (str, optional): The LLM provider to use ("openai" or "perplexity"). Defaults to "perplexity".
            model (str, optional): The model name to use. Defaults to provider-specific default ("gpt-4o-mini" for OpenAI, "sonar" for Perplexity).
            temperature (float, optional): The temperature setting for the model. Defaults to 0.
        Raises:
            ValueError: If an unknown provider is specified.
        """
        load_dotenv()
        self.provider = provider.lower()
        logger.info(f"Initializing LLMClient with provider: {self.provider}, model: {model if model else "default"}, temperature: {temperature}")

        if self.provider == "openai":
            logger.info("Using OpenAI provider")
            self.llm = ChatOpenAI(model=model or "gpt-4o-mini", temperature=temperature)
        
        elif self.provider == "perplexity":
            logger.info("Using Perplexity provider")
            self.llm = ChatPerplexity(model=model or "sonar", temperature=temperature)
        else:
            logger.error(f"Unknown provider: {provider}")
            raise ValueError(f"Unknown provider: {provider}")

    def run(self, prompt: str):
        """
        Executes the LLM (Large Language Model) with the provided prompt and returns the response content as a string.

        Args:
            prompt (str): The input prompt to be sent to the LLM.

        Returns:
            str: The content of the LLM's response.
        """
        logger.info(f"Running LLM with prompt: {prompt}")
        res = self.llm.invoke(prompt)
        logger.info(f"Received response: {res.content}")
        return str(res.content)
    
    def set_provider(self, provider: str):
        """
        Sets the provider for the client.

        Args:
            provider (str): The name of the provider to set. The value will be converted to lowercase.

        """
        logger.info(f"Setting provider to: {provider}")
        self.provider = provider.lower()

if __name__ == "__main__":
    client = LLMClient(provider="perplexity")
    print("Perplexity:", client.run("Hello from Perplexity!"))