from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from src.config.models import MODEL_PROVIDER_MAPPING
from src.services.summarize.summarizer import ZeroShotSummarizer
from src.services.postprocessing.operations import (
    SimplifyProcessor,
    ShortenProcessor,
    RephraseProcessor,
)
from PyPDF2 import PdfReader

app = FastAPI()

# ===== CORS setup =====
origins = [
    "http://localhost:3000",  # React dev server
    # "https://your-production-frontend.com"  # add your hosted frontend later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # allow all headers
)

PLACEHOLDER_SUMMARY = """## The "Attention" Trick That Changed AI Forever Imagine a world where language barriers crumble, where computers understand and generate text with uncanny human-like fluency, and where complex scientific problems are solved faster than ever before. This isn't science fiction; it's the reality we're rapidly approaching, thanks in no small part to a groundbreaking paper published in 2017 by Google Brain researchers: "Attention Is All You Need." This paper introduced the Transformer architecture, a revolutionary design that has since become the backbone of nearly every major advancement in artificial intelligence, especially in the realm of language. Let's dive into why this seemingly technical paper sparked an AI revolution. ### Why Our AI Brains Needed a Speed Boost Before the Transformer, the reigning champions for tasks involving sequences – like translating languages or predicting the next word in a sentence – were models called Recurrent Neural Networks (RNNs), particularly their more sophisticated cousins, LSTMs and GRUs. These models worked by processing information one step at a time, much like reading a book word by word, remembering only the previous word to understand the current one. While powerful, this sequential processing had a major drawback: it was inherently slow. If you have a very long sentence, the model has to wait for each word to be processed before moving to the next. This meant training these models took an enormous amount of time, especially for complex tasks, and they struggled to efficiently grasp connections between words that were far apart in a sentence. Think of it like trying to remember the beginning of a very long paragraph while you're reading the last sentence – it's tough! Other attempts to speed things up using convolutional networks (like those used for image processing) could process things in parallel, but they still struggled to efficiently connect distant parts of a sequence. Researchers knew there had to be a better way to help AI models understand the full context of a sentence, not just its immediate neighbors, and do it much faster. ### The 'Attention' Trick That Changed AI Forever The brilliant insight of the Transformer paper was to completely ditch the old, sequential way of doing things. Instead of processing words one by one, the Transformer introduced a radical new approach: **attention mechanisms, and nothing else.** Imagine you're reading a complex sentence. When you encounter a pronoun like "it," your brain instantly knows to look back at the relevant noun that "it" refers to. That's essentially what the Transformer's "self-attention" mechanism does. For every word in a sentence, the model simultaneously looks at *all* other words in that same sentence and calculates how important each of them is to understanding the current word. It's like having a super-fast internal cross-referencing system that instantly highlights the most relevant connections. But it gets even smarter. The Transformer doesn't just have one "attention" mechanism; it has **Multi-Head Attention**. This is like having several expert readers, each focusing on different aspects of the sentence at the same time. One "head" might focus on grammatical relationships, another on semantic meaning, and yet another on contextual nuances. By combining these multiple perspectives, the model gains a much richer and more nuanced understanding of the entire sequence. Since the model no longer processes words in order, the researchers also cleverly added "positional encodings" – mathematical signals that tell the model where each word sits in the sequence. This ensures the model knows the difference between "dog bites man" and "man bites dog." The results were astounding: * **Unprecedented Speed:** By allowing parallel processing, the Transformer could be trained significantly faster. For instance, it achieved state-of-the-art results on English-to-French translation in just 3.5 days on eight GPUs, a mere fraction of the time and cost of previous best models. * **Superior Quality:** It didn't just get faster; it got better. The Transformer achieved new state-of-the-art scores on challenging machine translation tasks, producing more accurate and natural-sounding translations. * **Versatility:** The architecture proved its mettle beyond translation, successfully tackling other complex language tasks like parsing sentences. This elegant design, relying solely on attention, proved to be a monumental breakthrough, offering a powerful, efficient, and highly parallelizable way for AI to understand and generate sequences. ### Powering the Future: From Chatbots to Scientific Discovery The impact of the Transformer architecture cannot be overstated. It didn't just improve existing AI; it fundamentally reshaped the landscape of artificial intelligence. The "Attention Is All You Need" paper laid the groundwork for what we now know as **Large Language Models (LLMs)**. Every major AI breakthrough you've heard about in recent years – from the conversational prowess of ChatGPT and Google Bard to the sophisticated text generation of GPT-3 and the contextual understanding of BERT – is built upon the Transformer. Here's how this single architectural innovation has rippled through society: * **Revolutionizing Communication:** Machine translation has become vastly more accurate and instantaneous, breaking down language barriers for global communication and commerce. AI-powered chatbots and virtual assistants are more intelligent and helpful, understanding complex queries and providing coherent responses. * **Unleashing Creativity:** The ability of Transformers to generate human-quality text has opened doors for creative writing, content generation, and even code development, assisting professionals across various industries. * **Accelerating Scientific Discovery:** Beyond language, the attention mechanism has proven incredibly powerful in other domains. Google's DeepMind used a Transformer-like architecture in AlphaFold, a revolutionary AI that predicts protein structures with unprecedented accuracy, accelerating drug discovery and our understanding of biology. * **Democratizing Advanced AI:** The increased efficiency and parallelization mean that developing and deploying powerful AI models is more accessible, fostering innovation across a wider range of researchers and companies. In essence, the Transformer didn't just give AI a speed boost; it gave it a new way to think, to connect ideas across vast distances in data, and to learn with unparalleled efficiency. It's the silent engine behind much of the AI revolution we're experiencing today, continually pushing the boundaries of what machines can understand, create, and achieve."""


# ===== Input models =====
class Input(BaseModel):
    text: str
    model: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    method: str | None = None
    intended_audience: str | None = None
    summary_style: str | None = None


class ParsePDFInput(BaseModel):
    parser_type: str = "PyPDF2"  # Options: "PyPDF2", "PDF Plumber", "OCR"


# ===== Summarize route =====
@app.post("/summarize")
def summarize(data: Input):

    text = data.text
    model = data.model or "gpt-4"
    temperature = data.temperature or 0.0
    top_p = data.top_p or 0.05
    method = data.method or "Default"
    intended_audience = data.intended_audience or "general"
    summary_style = data.summary_style or "concise"

    provider = MODEL_PROVIDER_MAPPING[model]

    # Create summarizer based on method
    if method in ["📚 Retrieval-Augmented Generation (RAG)", "RAG"]:
        from src.services.summarize.summarizer import RAGSummarizer

        summarizer = RAGSummarizer(
            provider=provider, model=model, temperature=int(temperature), top_p=top_p
        )
    else:
        # Default to ZeroShotSummarizer for other methods
        summarizer = ZeroShotSummarizer(
            provider=provider, model=model, temperature=temperature, top_p=top_p
        )

    # Get base summary
    base_summary = summarizer.summarize(text)

    # Apply audience and style modifications if needed
    if intended_audience != "general" or summary_style != "concise":
        # Create a post-processing prompt to adjust for audience and style
        audience_map = {
            "general": "general readers with no technical background",
            "experts": "subject matter experts and researchers",
            "students": "undergraduate and graduate students",
        }

        style_map = {
            "concise": "Keep it concise and to the point",
            "detailed": "Provide comprehensive details and explanations",
            "bullet_points": "Format the output as clear bullet points",
        }

        audience_text = audience_map.get(intended_audience, "general readers")
        style_text = style_map.get(summary_style, "Keep it concise")

        adjustment_prompt = f"""
        Please adjust the following summary for {audience_text}.
        {style_text}.
        
        Original Summary:
        {base_summary}
        
        Adjusted Summary:
        """

        # Use the same model to adjust the summary
        adjusted_summary = summarizer.run(adjustment_prompt)
        result = {"summary": adjusted_summary}
    else:
        result = {"summary": base_summary}

    return result


# ===== PDF Parsing route =====


@app.post("/parse_pdf")
async def parse_pdf(
    file: UploadFile = File(...), parser_type: str = Form(default="PyPDF2")
):
    try:
        if parser_type == "PyPDF2":
            # Original PyPDF2 method
            pdf_reader = PdfReader(file.file)
            parsed_text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    parsed_text += extracted + "\n"

            return {
                "parsed_text": parsed_text.strip(),
                "parser_used": "PyPDF2",
                "success": True,
                "message": "Successfully parsed with PyPDF2",
            }

        elif parser_type == "PDF Plumber":
            # PDF Plumber method (more advanced text extraction)
            try:
                import pdfplumber
                import io

                # Read the file into bytes and create BytesIO object
                file_bytes = await file.read()
                file_obj = io.BytesIO(file_bytes)

                parsed_text = ""
                with pdfplumber.open(file_obj) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            parsed_text += text + "\n"

                return {
                    "parsed_text": parsed_text.strip(),
                    "parser_used": "PDF Plumber",
                    "success": True,
                    "message": "Successfully parsed with PDF Plumber",
                }
            except ImportError:
                # Fallback to PyPDF2 if pdfplumber is not installed
                await file.seek(0)  # Reset file pointer
                pdf_reader = PdfReader(file.file)
                parsed_text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        parsed_text += extracted + "\n"

                return {
                    "parsed_text": parsed_text.strip(),
                    "parser_used": "PyPDF2 (PDF Plumber not available)",
                    "success": True,
                    "message": "PDF Plumber not installed, fell back to PyPDF2",
                }

        elif parser_type == "OCR":
            # OCR method for scanned PDFs
            try:
                import pytesseract
                from pdf2image import convert_from_bytes
                from PIL import Image
                import io

                # Convert PDF pages to images
                file_bytes = await file.read()
                images = convert_from_bytes(file_bytes)

                parsed_text = ""
                for i, image in enumerate(images):
                    # Use OCR to extract text from image
                    text = pytesseract.image_to_string(image, lang="eng")
                    if text.strip():
                        parsed_text += f"Page {i+1}:\n{text}\n\n"

                return {
                    "parsed_text": parsed_text.strip(),
                    "parser_used": "OCR (Tesseract)",
                    "success": True,
                    "message": "Successfully parsed with OCR",
                }

            except ImportError as e:
                # Fallback to PyPDF2 if OCR dependencies are not installed
                await file.seek(0)  # Reset file pointer
                pdf_reader = PdfReader(file.file)
                parsed_text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        parsed_text += extracted + "\n"

                return {
                    "parsed_text": parsed_text.strip(),
                    "parser_used": "PyPDF2 (OCR not available)",
                    "success": True,
                    "message": f"OCR dependencies not installed ({str(e)}), fell back to PyPDF2",
                }

        else:
            # Invalid parser type, default to PyPDF2
            pdf_reader = PdfReader(file.file)
            parsed_text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    parsed_text += extracted + "\n"

            return {
                "parsed_text": parsed_text.strip(),
                "parser_used": "PyPDF2 (default)",
                "success": True,
                "message": f"Unknown parser type '{parser_type}', used PyPDF2 as default",
            }

    except Exception as e:
        return {
            "parsed_text": "",
            "parser_used": "None",
            "success": False,
            "message": f"Error parsing PDF: {str(e)}",
        }


# ===== Shorten route =====
@app.post("/shorten")
def shorten(data: Input):
    text = data.text
    model = data.model or "gpt-4"
    temperature = data.temperature or 0.0
    top_p = data.top_p or 0.05
    provider = MODEL_PROVIDER_MAPPING[model]
    processor = ShortenProcessor(provider=provider, model=model)
    result = {"summary": processor.process(text)}
    return result


# Simplify Route
@app.post("/simplify")
def simplify(data: Input):
    text = data.text
    model = data.model or "gpt-4"
    temperature = data.temperature or 0.0
    top_p = data.top_p or 0.05
    provider = MODEL_PROVIDER_MAPPING[model]
    processor = SimplifyProcessor(provider=provider, model=model)
    result = {"summary": processor.process(text)}
    return result


# Rephrase Route
@app.post("/rephrase")
def rephrase(data: Input):
    text = data.text
    model = data.model or "gpt-4"
    temperature = data.temperature or 0.0
    top_p = data.top_p or 0.05
    provider = MODEL_PROVIDER_MAPPING[model]
    processor = RephraseProcessor(provider=provider, model=model)
    result = {"summary": processor.process(text)}
    return result
