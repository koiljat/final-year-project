import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_perplexity import ChatPerplexity
import logging
from config.models import Provider

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, provider="openai", model=None, temperature=0.0, **kwargs):
        """
        Initializes the LLM client with the specified provider, model, and temperature.
        Loads environment variables using `load_dotenv()`. Sets up the language model interface based on the chosen provider. Raises a ValueError for unknown providers.

        Args:
            provider (str, optional): The LLM provider to use ("openai" or "perplexity"). Defaults to "perplexity".
            model (str, optional): The model name to use. Defaults to provider-specific default ("gpt-4o-mini" for OpenAI, "sonar" for Perplexity).
            temperature (float, optional): The temperature setting for the model. Defaults to 0.
        Raises:
            ValueError: If an unknown provider is specified.
        """
        load_dotenv()
        self.provider = provider.lower()
        self.model = model
        logger.info(
            f"Initializing LLMClient with provider: {self.provider}, model: {self.model if self.model else 'default'}, temperature: {temperature}"
        )

        if self.provider == "openai":
            logger.info("Using OpenAI provider")
            self.llm = ChatOpenAI(
                model=self.model or "gpt-4o-mini",
                temperature=temperature,
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        elif self.provider == "perplexity":
            logger.info("Using Perplexity provider")
            self.llm = ChatPerplexity(
                model=self.model or "sonar",
                temperature=temperature,
                pplx_api_key=os.getenv("PERPLEXITY_API_KEY"),
                timeout=30,
            )
        elif self.provider == "gemini":
            logger.info("Using Gemini provider")
            self.llm = ChatGoogleGenerativeAI(
                model=self.model or "gemini-2.5-flash",
                temperature=temperature,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
        else:
            logger.error(f"Unknown provider: {provider}")
            raise ValueError(f"Unknown provider: {provider}")

    def run(self, prompt: str) -> str:
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

    def set_provider(self, provider):
        logger.info(f"Setting provider to: {provider}")
        if isinstance(provider, str):
            self.provider = provider.lower()
        elif isinstance(provider, Provider):
            self.provider = provider.name.lower()
        else:
            raise ValueError(f"Unknown provider type: {type(provider)}")

    def set_model(self, model: str):
        """
        Sets the model for the client.

        Args:
            model (str): The name of the model to set.

        """
        logger.info(f"Setting model to: {model}")
        self.model = model


if __name__ == "__main__":
    client = LLMClient(provider="openai")
