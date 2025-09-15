"""
Data models and configuration classes for the Streamlit Summarization App.
These dataclasses provide type safety and structure for data passed between components.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class SummarizationMethod(Enum):
    """Enumeration of available summarization methods."""
    DEFAULT = "Default"
    RAG = "RAG" 
    MAP_REDUCE = "MapReduce"


class PostProcessingAction(Enum):
    """Enumeration of post-processing actions."""
    SIMPLIFY = "Simplify"
    SHORTEN = "Shorten"
    EXPAND = "Expand"
    REPHRASE = "Rephrase"


class Provider(Enum):
    """Enumeration of AI model providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"


@dataclass
class TextMetrics:
    """Metrics calculated from text analysis."""
    word_count: int
    character_count: int
    sentence_count: int = 0
    paragraph_count: int = 0
    estimated_read_time_minutes: int = 0
    
    def __post_init__(self):
        """Calculate derived metrics after initialization."""
        if self.estimated_read_time_minutes == 0:
            # Estimate 200 words per minute reading speed
            self.estimated_read_time_minutes = max(1, self.word_count // 200)


@dataclass
class SummaryResult:
    """Result object containing summary content and metadata."""
    content: str
    processing_time: float
    method_used: str
    metrics: Dict[str, Any]
    paragraphs: List[str] = field(default_factory=list)
    original_metrics: Optional[TextMetrics] = None
    summary_metrics: Optional[TextMetrics] = None
    
    def __post_init__(self):
        """Process content into paragraphs if not already done."""
        if not self.paragraphs and self.content:
            # Split content into paragraphs, handling both \n\n and single sentences
            paragraphs = [p.strip() for p in self.content.split('\n\n') if p.strip()]
            if not paragraphs:
                # Fallback: split by sentences and group
                sentences = self.content.split('. ')
                paragraphs = []
                for i in range(0, len(sentences), 3):
                    para = '. '.join(sentences[i:i+3])
                    if para and not para.endswith('.'):
                        para += '.'
                    if para:
                        paragraphs.append(para)
            self.paragraphs = paragraphs


@dataclass
class AppSettings:
    """Application settings and model configuration."""
    model_name: str = "gpt-4o"
    provider: Provider = Provider.OPENAI
    temperature: float = 0.0
    max_tokens: int = 3000
    top_p: float = 0.01
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    selected_method: SummarizationMethod = SummarizationMethod.DEFAULT
    
    # UI Settings
    show_advanced_settings: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for API calls."""
        return {
            'model': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
        }


@dataclass
class FileUploadResult:
    """Result of file upload processing."""
    content: str
    filename: str
    file_type: str
    file_size: int
    success: bool = True
    error_message: Optional[str] = None
    metrics: Optional[TextMetrics] = None
    
    def __post_init__(self):
        """Calculate metrics from content if successful."""
        if self.success and self.content and not self.metrics:
            words = len(self.content.split())
            chars = len(self.content)
            # Simple sentence count (rough estimate)
            sentences = len([s for s in self.content.split('.') if s.strip()])
            paragraphs = len([p for p in self.content.split('\n\n') if p.strip()])
            
            self.metrics = TextMetrics(
                word_count=words,
                character_count=chars,
                sentence_count=sentences,
                paragraph_count=max(1, paragraphs)
            )


@dataclass
class ProcessingStatus:
    """Track the status of summarization processing."""
    is_processing: bool = False
    current_step: str = ""
    progress_percentage: int = 0
    start_time: Optional[float] = None
    error_message: Optional[str] = None
    
    @property
    def has_error(self) -> bool:
        """Check if there's an error."""
        return self.error_message is not None


# Model name to provider mapping
MODEL_PROVIDER_MAPPING = {
    "gpt-5": Provider.OPENAI,
    "gpt-4.1": Provider.OPENAI,
    "gpt-4o": Provider.OPENAI,
    "gpt-4": Provider.OPENAI,
    "o4-mini": Provider.OPENAI,
    "gemini-2.5-flash": Provider.GEMINI,
    "sonar": Provider.PERPLEXITY,
}


# Method configuration with descriptions and icons
SUMMARIZATION_METHODS = {
    SummarizationMethod.DEFAULT: {
        "description": "Quick and efficient summarization",
        "icon": "⚡",
        "recommended_for": "General documents under 5000 words"
    },
    SummarizationMethod.RAG: {
        "description": "Retrieval-augmented generation for enhanced context",
        "icon": "🧠",
        "recommended_for": "Complex documents requiring deep understanding"
    },
    SummarizationMethod.MAP_REDUCE: {
        "description": "Hierarchical summarization for long documents",
        "icon": "🗂️",
        "recommended_for": "Very long documents (10,000+ words)"
    },
}


# Default session state values
DEFAULT_SESSION_STATE = {
    "summarize_input": "",
    "current_result": None,
    "processed_result": None,
    "result_ls": None,
    "processing_time": None,
    "original_word_count": 0,
    "summary_word_count": 0,
    "file_uploaded": False,
    "processing_status": None,
    "settings": AppSettings(),
}


def get_provider_for_model(model_name: str) -> Provider:
    """
    Get the provider for a given model name.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Provider enum value
    """
    return MODEL_PROVIDER_MAPPING.get(model_name, Provider.OPENAI)


def validate_settings(settings: AppSettings) -> List[str]:
    """
    Validate app settings and return list of validation errors.
    
    Args:
        settings: Settings to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not 0.0 <= settings.temperature <= 2.0:
        errors.append("Temperature must be between 0.0 and 2.0")
    
    if not 1 <= settings.max_tokens <= 4000:
        errors.append("Max tokens must be between 1 and 4000")
    
    if not 0.0 <= settings.top_p <= 1.0:
        errors.append("Top-p must be between 0.0 and 1.0")
    
    if not -2.0 <= settings.frequency_penalty <= 2.0:
        errors.append("Frequency penalty must be between -2.0 and 2.0")
    
    if not -2.0 <= settings.presence_penalty <= 2.0:
        errors.append("Presence penalty must be between -2.0 and 2.0")
    
    return errors