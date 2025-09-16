# Document Summarization System

**BT4101: B.Sc. (Business Analytics) Dissertation**

A comprehensive document summarization application that leverages Large Language Models (LLMs) to automatically generate structured summaries of research papers and academic documents.

## 📋 Overview

This project implements an intelligent document summarization system designed specifically for academic research papers. The application provides multiple summarization approaches and an intuitive web interface to help researchers quickly extract key insights from lengthy documents.

### Key Features

- **Multiple Summarization Methods**:
  - **Zero-Shot**: Direct summarization using pre-trained models
  - **RAG (Retrieval-Augmented Generation)**: Context-aware summarization with enhanced accuracy
  - **MapReduce**: Hierarchical summarization for long documents

- **File Format Support**:
  - PDF documents
  - Text files (.txt)
  - Markdown files (.md)
  - Rich Text Format (.rtf)

- **Structured Output**: Generates summaries organized into three key sections:
  - **Motivation**: Why the research problem matters
  - **Key Contribution**: Novel approaches, methods, or results
  - **Societal Implications**: Broader impact and relevance

- **Interactive Web Interface**: User-friendly Streamlit application with real-time editing capabilities
- **Performance Metrics**: Word count analysis and compression ratios
- **Multiple LLM Providers**: Support for OpenAI and Perplexity APIs

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API key for OpenAI or Perplexity

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/koiljat/final-year-project.git
   cd final-year-project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   > **Note**: If you encounter version compatibility issues, you may need to install compatible versions:
   ```bash
   pip install langchain>=0.2.0 langchain-openai>=0.1.0 langchain-community>=0.2.0 streamlit>=1.49.1 python-dotenv>=1.1.1 PyPDF2
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   ```

### Running the Application

1. **Start the Streamlit app**:
   ```bash
   streamlit run src/app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

## 💻 Usage

1. **Upload or Input Text**:
   - Upload a document using the file uploader in the sidebar
   - Or paste text directly into the input area

2. **Select Summarization Method**:
   - Choose from Default, RAG, or MapReduce methods
   - Configure API provider (OpenAI or Perplexity) in the sidebar

3. **Generate Summary**:
   - Click "Generate Summary" to process your document
   - View results with performance metrics

4. **Edit and Refine**:
   - Edit summary paragraphs directly in the interface
   - Apply post-processing options (Simplify, Custom Prompt, Shorten)

## 📁 Project Structure

```
final-year-project/
├── src/
│   ├── app.py                 # Main Streamlit application
│   ├── llm/
│   │   ├── llm_client.py      # LLM client implementations
│   │   └── summarize/
│   │       └── summarizer.py  # Summarization logic
│   └── prompts/
│       ├── prompt_manager.py  # Prompt management
│       └── prompts.yaml       # Prompt templates
├── notebooks/
│   └── 01_baseline_summarisation.ipynb  # Research experiments
├── requirements.txt           # Python dependencies
├── fyp_summarise.drawio      # System architecture diagram
└── README.md                 # This file
```

## 🛠 Technical Details

### Technologies Used

- **Frontend**: Streamlit for web interface
- **LLM Integration**: LangChain ecosystem
- **APIs**: OpenAI GPT models, Perplexity API
- **Document Processing**: PyPDF2 for PDF parsing
- **Environment Management**: python-dotenv

### Dependencies

- `langchain>=0.3.32,<0.4.0` - LLM framework
- `langchain_openai>=0.3.32,<0.4.0` - OpenAI integration
- `langchain_community>=0.3.32,<0.4.0` - Community extensions
- `streamlit>=1.49.1,<2.0.0` - Web application framework
- `python-dotenv>=1.1.1,<2.0.0` - Environment variable management

## 🎯 Academic Context

This project is developed as part of the BT4101 Business Analytics dissertation, focusing on:

- **Research Problem**: Efficient extraction of key information from academic literature
- **Methodology**: Comparative analysis of different LLM-based summarization approaches
- **Evaluation**: Performance metrics including compression ratios and processing times
- **Innovation**: Structured summarization tailored for academic research papers

## 📊 Features in Detail

### Summarization Methods

1. **Default (Zero-Shot)**: Direct summarization using model's inherent capabilities
2. **RAG**: Retrieval-augmented approach for context-aware summaries
3. **MapReduce**: Divide-and-conquer method for handling long documents

### Output Structure

Each summary is organized into three focused sections:
- **Motivation**: Research rationale and problem significance
- **Key Contribution**: Main findings, methods, or innovations
- **Societal Implications**: Real-world impact and applications

### Performance Monitoring

- Word count comparison (original vs. summary)
- Compression ratio calculation
- Processing time measurement
- Real-time metrics display

## 🔧 Configuration

### API Provider Selection

The application supports multiple LLM providers:
- **OpenAI**: Access to GPT models
- **Perplexity**: Alternative LLM provider with different capabilities

### Customization Options

- Creativity level adjustment (temperature parameter)
- Complexity level settings
- Custom prompt engineering
- Post-processing operations

## 🛠 Troubleshooting

### Common Issues

1. **Version Compatibility**: If you encounter dependency conflicts, try installing with:
   ```bash
   pip install --upgrade pip
   pip install langchain langchain-openai langchain-community streamlit python-dotenv PyPDF2
   ```

2. **API Key Issues**: Ensure your `.env` file is in the root directory and contains valid API keys:
   ```env
   OPENAI_API_KEY=sk-...
   PERPLEXITY_API_KEY=pplx-...
   ```

3. **Port Already in Use**: If port 8501 is busy, specify a different port:
   ```bash
   streamlit run src/app.py --server.port 8502
   ```

4. **File Upload Issues**: Ensure uploaded files are in supported formats (PDF, TXT, MD, RTF)

### System Requirements

- Python 3.8 or higher
- Stable internet connection for API calls
- Sufficient memory for document processing (recommended: 4GB+ RAM)

## 📈 Future Enhancements

- Additional file format support
- Batch processing capabilities
- Summary quality evaluation metrics
- Multi-language support
- Advanced prompt customization

## 📝 License

This project is developed for academic purposes as part of the BT4101 dissertation requirement.

## 🤝 Contributing

This is an academic project. For questions or discussions about the research, please contact the project author.

---

**Note**: This application requires valid API keys for LLM services. Ensure you have appropriate access and follow the respective providers' usage guidelines.
