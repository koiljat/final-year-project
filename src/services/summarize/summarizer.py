from services.llm_client import LLMClient
from prompts.prompt_manager import PromptManager
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Summarizer(LLMClient):
    """Base Summarizer class using LLMClient and PromptManager."""

    def __init__(self, model=None, temperature=0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)
        self.prompt_manager = PromptManager()

    def summarize(self, text: str, mode="default") -> str:
        prompt = self.prompt_manager.get(mode).format(text=text)
        return self.run(prompt)

    def split_by_paragraph(self, text: str) -> list[str]:
        return text.split("\n\n")


class ZeroShotSummarizer(Summarizer):
    """Zero-Shot Summarizer using predefined prompts."""

    def __init__(self, model=None, temperature=0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)

    def summarize(self, text: str) -> str:
        return super().summarize(text, mode="zero_shot")


class RAGSummarizer(Summarizer):
    """Retrieval-Augmented Generation (RAG) Summarizer.
    This summarizer splits the input text into chunks, creates an in-memory vector store,
    and retrieves relevant chunks for summarization.
    """

    def __init__(self, model=None, temperature=0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)

    def split_text(self, text: str, chunk_size=500, overlap=50):
        """Splits text into chunks for RAG."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
        return chunks

    def get_vector_store(self, texts):
        """Creates a vector store from text chunks."""
        load_dotenv()
        logging.info("Creating vector store from text chunks.")
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_texts(texts, embeddings)
        return vector_store

    def retrieve_relevant_chunks(self, vector_store, query, k=3):
        """Retrieves relevant text chunks from the vector store."""
        logging.info("Retrieving relevant chunks for the query.")
        docs = vector_store.similarity_search(query, k=k)
        return " ".join([doc.page_content for doc in docs])

    def summarize(self, text: str) -> str:
        chunks = self.split_text(text)
        vector_store = self.get_vector_store(chunks)
        relevant_text = self.retrieve_relevant_chunks(vector_store, text)
        logger.info("Summarizing the relevant text.")
        return super().summarize(relevant_text, mode="RAG")


class MapReduceSummarizer(Summarizer):
    """Map-Reduce Summarizer (Placeholder for future implementation)."""

    def __init__(self, model=None, temperature=0, **kwargs):
        super().__init__(model=model, temperature=temperature, **kwargs)

    def summarize(self, text: str) -> str:
        map_chunks = self.split_by_paragraph(text)
        # Placeholder for Map step
        intermediate_summaries = [
            super().summarize(chunk, mode="map") for chunk in map_chunks
        ]
        combined_summary = " ".join(intermediate_summaries)
        # Placeholder for Reduce step
        return super().summarize(combined_summary, mode="reduce")
