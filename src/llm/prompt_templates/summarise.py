DEFAULT_SUMMARY_PROMPT_TEMPLATE = """You are a helpful assistant that summarises research papers.
Given the following extract from a research paper, provide a concise summary in a single paragraph.

Your summary should focus on 3 points:
1. Motivation of the paper
2. Key Contribution 
3. Implications for the society

Extract: {text}
Summary:"""

RAG_SUMMARY_PROMPT_TEMPLATE = """You are a helpful assistant that summarises research papers.
Given the following extract from a research paper, provide a concise summary in a single paragraph.

Your summary should focus on 3 points:
1. Motivation of the paper
2. Key Contribution
3. Implications for the society

Extract: {text}
Summary:"""

MAP_REDUCE_SUMMARY_PROMPT_TEMPLATE = """You are a helpful assistant that summarises research papers.
Given the following extract from a research paper, provide a concise summary in a single paragraph.

Your summary should focus on 3 points:
1. Motivation of the paper
2. Key Contribution
3. Implications for the society

Extract: {text}
Summary:"""

prompt_mapping = {
    "default": DEFAULT_SUMMARY_PROMPT_TEMPLATE,
    "RAG": RAG_SUMMARY_PROMPT_TEMPLATE,
    "map_reduce": MAP_REDUCE_SUMMARY_PROMPT_TEMPLATE
}