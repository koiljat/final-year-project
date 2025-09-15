# services/postprocessing/registry.py
from dataclasses import dataclass
from typing import Any
from services.postprocessing.operations import SimplifyProcessor, ShortenProcessor, RephraseProcessor, ExpandProcessor

@dataclass
class PostProcessorInfo:
    cls: Any
    desc: str

POST_PROCESSORS = {
    "Simplify": PostProcessorInfo(cls=SimplifyProcessor, desc="Simplify the text"),
    "Shorten": PostProcessorInfo(cls=ShortenProcessor, desc="Shorten the text"),
    "Rephrase": PostProcessorInfo(cls=RephraseProcessor, desc="Rephrase the text"),
    "Expand": PostProcessorInfo(cls=ExpandProcessor, desc="Expand the text"),
}

def get_post_processor(name: str, **kwargs):
    info = POST_PROCESSORS.get(name)
    if not info:
        raise ValueError(f"Unknown post-processing operation: {name}")
    return info.cls(**kwargs)
