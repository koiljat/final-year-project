from typing import Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from prompts.prompt_manager import PromptManager


class TextSummarizer:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.prompt_manager = PromptManager()
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None

    def build_vectorstore(self, text: str):
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)

    def summarize(
        self, text: str, type: str = "default", retrieval_query: Optional[str] = None
    ) -> str:

        if type == "RAG":
            if self.vectorstore is None:
                self.build_vectorstore(text)

            retriever = self.vectorstore.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )

            if retrieval_query is None:
                retrieval_query = (
                    "Retrieve the most relevant sections for summarization"
                )
            retrieved_docs = retriever.get_relevant_documents(retrieval_query)

            context = "\n\n".join([doc.page_content for doc in retrieved_docs])

            prompt_template = self.prompt_manager.get("RAG")
            prompt = prompt_template.format(text=context)

            res = self.llm.invoke(prompt)
            return str(res.content)

        elif type == "MapReduce":
            pass

        else:
            prompt_template = self.prompt_manager.get("default")
            prompt = prompt_template.format(text=text)
            res = self.llm.invoke(prompt)
            return str(res.content)

    def split_by_paragraph(self, text: str) -> list[str]:
        return text.split("\n\n")


if __name__ == "__main__":
    load_dotenv()
#     summarizer = TextSummarizer()
#     sample_prompt = """The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.
# """

#     prompt_mapping = {
#         "default": "Summarize the following text:\n\n{text}",
#         "RAG": "Here are some retrieved sections:\n\n{context}\n\nWrite a concise summary of only the financial analysis parts.",
#     }

#     summarizer = TextSummarizer()

#     big_text = sample_prompt
#     summary = summarizer.summarize(big_text)
#     print(summary)
