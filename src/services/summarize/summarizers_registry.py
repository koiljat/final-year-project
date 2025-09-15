# summarizers_registry.py
from dataclasses import dataclass
from typing import Any
from services.summarize.summarizer import ZeroShotSummarizer, RAGSummarizer, MapReduceSummarizer

@dataclass
class SummarizerInfo:
    cls: Any
    desc: str
    icon: str

SUMMARIZERS = {
    "Default": SummarizerInfo(
        cls=ZeroShotSummarizer,
        desc="Quick and efficient summarization",
        icon="⚡",
    ),
    "RAG": SummarizerInfo(
        cls=RAGSummarizer,
        desc="Retrieval-augmented generation for enhanced context",
        icon="🧠",
    ),
    "MapReduce": SummarizerInfo(
        cls=MapReduceSummarizer,
        desc="Hierarchical summarization for long documents",
        icon="🗂️",
    ),
}

def get_summarizer(name: str, **kwargs):
    info = SUMMARIZERS.get(name, SUMMARIZERS["Default"])
    return info.cls(**kwargs)
