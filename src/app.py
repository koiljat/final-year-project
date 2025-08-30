import streamlit as st
import time
from typing import Optional, Dict, Any
from llm.summarise import TextSummarizer
import sys
import os
import traceback



# Initialize the summarizer
@st.cache_resource
def get_summarizer():
    """Initialize and cache the text summarizer."""
    return TextSummarizer()

class SummarizationApp:
    """Professional text summarization application."""
    
    def __init__(self):
        self.summarizer = get_summarizer()
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Final Year Project Demo",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .section-header {
            color: #2c3e50;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e8f4fd;
            padding-bottom: 0.5rem;
        }
        
        .result-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            border-left: 4px solid #1f77b4;
            margin: 1rem 0;
        }
        
        .metrics-container {
            background-color: #e8f4fd;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize session state variables."""
        session_defaults = {
            'current_result': None,
            'processed_result': None,
            'processing_time': None,
            'original_word_count': 0,
            'summary_word_count': 0,
            'compression_ratio': 0
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def calculate_metrics(self, original_text: str, summary_text: str) -> Dict[str, Any]:
        """Calculate text processing metrics."""
        original_words = len(original_text.split())
        summary_words = len(summary_text.split())
        compression_ratio = (1 - summary_words / original_words) * 100 if original_words > 0 else 0
        
        return {
            'original_words': original_words,
            'summary_words': summary_words,
            'compression_ratio': round(compression_ratio, 1)
        }
    
    def display_metrics(self, metrics: Dict[str, Any], processing_time: float):
        """Display processing metrics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Original Words", f"{metrics['original_words']:,}")
        with col2:
            st.metric("Summary Words", f"{metrics['summary_words']:,}")
        with col3:
            st.metric("Compression", f"{metrics['compression_ratio']}%")
        with col4:
            st.metric("Processing Time", f"{processing_time:.2f}s")
    
    def process_text(self, method: str, text: str) -> Optional[str]:
        """Process text using the selected summarization method."""
        try:
            start_time = time.time()
            
            if method == "Baseline Summarize":
                result = self.summarizer.summarize(text)
            elif method == "RAG Summarize":
                result = self.summarizer.summarize(text, type="RAG")
            elif method == "MapReduce Summarize":
                # Placeholder for MapReduce implementation
                result = "🚧 MapReduce summarization feature coming soon. This method will handle very large documents by processing them in chunks."
            else:
                st.error(f"Unknown summarization method: {method}")
                return None
            
            processing_time = time.time() - start_time
            st.session_state['processing_time'] = processing_time
            
            # Calculate and store metrics
            metrics = self.calculate_metrics(text, result)
            st.session_state['original_word_count'] = metrics['original_words']
            st.session_state['summary_word_count'] = metrics['summary_words']
            st.session_state['compression_ratio'] = metrics['compression_ratio']
            
            return result
            
        except Exception as e:
            st.error(f"Error during processing: {str(e)}")
            st.text(traceback.format_exc())  # shows full traceback in Streamlit
            return None
    
    def apply_post_processing(self, operation: str, text: str) -> str:
        """Apply post-processing operations to the text."""
        try:
            start_time = time.time()
            
            operations = {
                "Simplify": "✨ Simplified for better readability: ",
                "Manual Prompt": "🎯 Custom processing applied: ",
                "Shorten": "📝 Further condensed: "
            }
            
            # Simulate processing time
            time.sleep(0.5)
            
            processing_time = time.time() - start_time
            result = f"{operations.get(operation, '')} {text}"
            
            return result
            
        except Exception as e:
            st.error(f"Error during post-processing: {str(e)}")
            
            return text
    
    def render_sidebar(self):
        """Render the sidebar with additional options."""
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            
            # Summarization parameters
            st.markdown("**Summarization Parameters**")
            temperature = st.slider("Creativity Level (Temperature)", 0.1, 1.0, 0.7, 0.1)
            complexity = st.slider("Complexity Level", 1, 5, 3)

            st.markdown("---")
            
            st.markdown("### 📁 File Upload")
            uploaded_file = st.file_uploader(
                "Upload a text file",
                type=['txt', 'md', 'rtf'],
                help="Upload a text file to summarize its contents"
            )
            
            if uploaded_file:
                content = str(uploaded_file.read(), "utf-8")
                st.success(f"File loaded: {len(content.split())} words")
                return content
            
    
    def render_main_interface(self):
        """Render the main application interface."""
        # Header
        st.markdown('<h2 class="main-header">Summarisation & Simplification of Domain Specific Documents</h2>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Transform lengthy content into concise, meaningful summaries using advanced AI techniques</p>', unsafe_allow_html=True)
        
        # Get uploaded content from sidebar
        uploaded_content = self.render_sidebar()
        
        # Main content area
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<h2 class="section-header">📝 Input Configuration</h2>', unsafe_allow_html=True)
            
            # Method selection
            summarization_method = st.selectbox(
                "**Select Summarization Method:**",
                ["Baseline Summarize", "RAG Summarize", "MapReduce Summarize"],
                help="Choose the AI method for text summarization"
            )
            
            # Text input
            input_key = f"{summarization_method.lower().replace(' ', '_')}_input"
            default_text = uploaded_content if uploaded_content else ""
            
            summarize_input = st.text_area(
                "**Enter or paste your content:**",
                value=default_text,
                key=input_key,
                height=300,
                help="Paste your text here or upload a file using the sidebar"
            )
            
            # Display input statistics
            if summarize_input:
                word_count = len(summarize_input.split())
                char_count = len(summarize_input)
                st.caption(f"📊 Input: {word_count:,} words • {char_count:,} characters")
            
            # Action buttons
            st.markdown("**Actions:**")
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
                    if summarize_input.strip():
                        with st.spinner("🔄 Processing your content..."):
                            result = self.process_text(summarization_method, summarize_input)
                            if result:
                                st.session_state["current_result"] = result
                                st.session_state["result_ls"] = self.summarizer.split_by_paragraph(result)

            with col_btn2:
                if st.button("🗑️ Clear All", use_container_width=True):
                    for key in ['current_result', 'processed_result', 'result_ls']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

            
            if st.session_state.get("current_result"):
                st.success("✅ Summary generated successfully!")
        
        with col2:
            st.markdown('<h2 class="section-header">📄 Results</h2>', unsafe_allow_html=True)
            
            if "result_ls" in st.session_state:
                edited_results = []
                for i, para in enumerate(st.session_state["result_ls"]):
                    
                    min_height = 100
                    extra_per_50_words = 100
                    calculated_height = min_height + (len(para.split()) // 50) * extra_per_50_words

                    edited_text = st.text_area(
                        f"Paragraph {i+1}", 
                        value=para, 
                        key=f"para_{i}", 
                        height=calculated_height
                    )
                    edited_results.append(edited_text)

                # Optionally store back the edited version
                st.session_state["result_ls"] = edited_results
                
                # Display metrics
                if st.session_state.get('processing_time'):
                    metrics = {
                        'original_words': st.session_state.get('original_word_count', 0),
                        'summary_words': st.session_state.get('summary_word_count', 0),
                        'compression_ratio': st.session_state.get('compression_ratio', 0)
                    }
                    self.display_metrics(metrics, st.session_state['processing_time'])
                
                # Post-processing options
                st.markdown("**Post-Processing Options:**")
                col_post1, col_post2, col_post3 = st.columns(3)
                
                with col_post1:
                    if st.button("✨ Simplify", use_container_width=True):
                        with st.spinner("Simplifying..."):
                            processed = self.apply_post_processing("Simplify", st.session_state["current_result"])
                            st.session_state["processed_result"] = processed
                
                with col_post2:
                    if st.button("🎯 Custom Prompt", use_container_width=True):
                        with st.spinner("Applying custom processing..."):
                            processed = self.apply_post_processing("Manual Prompt", st.session_state["current_result"])
                            st.session_state["processed_result"] = processed
                
                with col_post3:
                    if st.button("📝 Shorten More", use_container_width=True):
                        with st.spinner("Further shortening..."):
                            processed = self.apply_post_processing("Shorten", st.session_state["current_result"])
                            st.session_state["processed_result"] = processed
                
            else:
                st.markdown("**Result will appear here.**  \n Generate a summary to see the output in this section.")

    def run(self):
        """Run the Streamlit application."""
        self.render_main_interface()

if __name__ == "__main__":
    app = SummarizationApp()
    app.run()