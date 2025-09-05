import streamlit as st
import time
from typing import Optional, Dict, Any
from llm.summarize.summarizer import RAGSummarizer, ZeroShotSummarizer, MapReduceSummarizer
import traceback
import PyPDF2

class SummarizationApp:
    def __init__(self):
        self.summarizers = {
            "Default": ZeroShotSummarizer(),
            "RAG": RAGSummarizer(),
            "MapReduce": MapReduceSummarizer(),
        }
        self.setup_page_config()
        self.initialize_session_state()

    # ---------------------------
    # Page Configuration & Styles
    # ---------------------------
    def setup_page_config(self):
        st.set_page_config(
            page_title="Final Year Project Demo",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        st.markdown(
            """
        <style>
        .main-header {text-align:center;color:#1f77b4;font-size:2.5rem;font-weight:600;margin-bottom:1rem;}
        .subtitle {text-align:center;color:#666;font-size:1.1rem;margin-bottom:2rem;}
        .section-header {color:#2c3e50;font-size:1.4rem;font-weight:600;margin-bottom:1rem;border-bottom:2px solid #e8f4fd;padding-bottom:0.5rem;}
        .result-container {background-color:#f8f9fa;border-radius:10px;padding:1.5rem;border-left:4px solid #1f77b4;margin:1rem 0;}
        .metrics-container {background-color:#e8f4fd;border-radius:8px;padding:1rem;margin:1rem 0;}
        .stButton > button {width:100%;border-radius:8px;font-weight:600;transition:all 0.3s ease;}
        .stButton > button:hover {transform:translateY(-2px);box-shadow:0 4px 8px rgba(0,0,0,0.1);}
        </style>
        """,
            unsafe_allow_html=True,
        )

    # ---------------------------
    # Session State Initialization
    # ---------------------------
    def initialize_session_state(self):
        defaults = {
            "summarize_input": "",
            "current_result": None,
            "processed_result": None,
            "result_ls": None,
            "processing_time": None,
            "original_word_count": 0,
            "summary_word_count": 0,
            "compression_ratio": 0,
            "file_uploaded": False, 
            "provider": "perplexity", #TODO: change to openais
            #TODO: Add temperature and OpenAI paramters
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # ---------------------------
    # Metrics Calculation & Display
    # ---------------------------
    def calculate_metrics(
        self, original_text: str, summary_text: str
    ) -> Dict[str, Any]:
        original_words = len(original_text.split())
        summary_words = len(summary_text.split())
        compression_ratio = (
            (1 - summary_words / original_words) * 100 if original_words else 0
        )
        return {
            "original_words": original_words,
            "summary_words": summary_words,
            "compression_ratio": round(compression_ratio, 1),
        }

    def display_metrics(self, metrics: Dict[str, Any], processing_time: float):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Original Words", f"{metrics['original_words']:,}")
        col2.metric("Summary Words", f"{metrics['summary_words']:,}")
        col3.metric("Compression", f"{metrics['compression_ratio']}%")
        col4.metric("Processing Time", f"{processing_time:.2f}s")

    # ---------------------------
    # Text Processing
    # ---------------------------
    def process_text(self, method: str, text: str) -> Optional[str]:
        try:
            start = time.time()
            if method in self.summarizers:
                self.summarizers[method].set_provider(st.session_state["provider"])
                result = self.summarizers[method].summarize(text)
            else:
                st.error(f"Unknown method: {method}")
                return None

            st.session_state["processing_time"] = time.time() - start
            metrics = self.calculate_metrics(text, result)
            st.session_state.update(
                {
                    "original_word_count": metrics["original_words"],
                    "summary_word_count": metrics["summary_words"],
                    "compression_ratio": metrics["compression_ratio"],
                }
            )
            return result

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.text(traceback.format_exc())
            return None

    # ---------------------------
    # Post-Processing
    # ---------------------------
    def apply_post_processing(self, operation: str, text: str) -> str:
        try:
            operations = {
                "Simplify": "✨ Simplified: ",
                "Manual Prompt": "🎯 Custom: ",
                "Shorten": "📝 Shortened: ",
            }
            time.sleep(0.5)
            return f"{operations.get(operation, '')} {text}"
        except Exception as e:
            st.error(f"Post-processing error: {str(e)}")
            return text

    # ---------------------------
    # Sidebar
    # ---------------------------
    def render_sidebar(self):
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            st.slider("Creativity Level", 0.1, 1.0, 0.7, 0.1)
            st.slider("Complexity Level", 1, 5, 3)
            st.markdown("---")
            st.session_state["provider"] = st.selectbox(
                "Select API Provider:",
                ["perplexity", "openai"],
            )
            st.markdown("---")
            st.markdown("### 📁 Upload File")
            file = st.file_uploader("Upload a text file", type=["txt", "md", "rtf", "pdf"])
            if file:
                content = ""
                if file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        content += page.extract_text() or ""
                else:
                    content = str(file.read(), "utf-8")

                st.success(f"File loaded: {len(content.split())} words")
                st.session_state["summarize_input"] = content
                st.session_state["file_uploaded"] = True
            else:
                st.session_state["file_uploaded"] = False

    # ---------------------------
    # Main Interface
    # ---------------------------
    def render_main_interface(self):
        st.markdown(
            '<h2 class="main-header">Summarisation & Simplification</h2>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="subtitle">Convert long documents into concise, meaningful summaries</p>',
            unsafe_allow_html=True,
        )
        self.render_sidebar()

        # Input & method
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(
                '<h2 class="section-header">📝 Input</h2>', unsafe_allow_html=True
            )
            method = st.selectbox(
                "Select Summarization Method:",
                ["Default", "RAG", "MapReduce"],
            )
            summarize_input = st.text_area(
                "Enter or paste content:",
                value=st.session_state["summarize_input"],
                key="summarize_input",
                height=300,
                disabled=st.session_state.get("file_uploaded", False),
            )

            if summarize_input:
                st.caption(
                    f"📊 Input: {len(summarize_input.split()):,} words • {len(summarize_input):,} characters"
                )

            # Actions
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("🚀 Generate Summary", use_container_width=True):
                    if summarize_input.strip():
                        with st.spinner("Processing..."):
                            result = self.process_text(method, summarize_input)
                            if result:
                                st.session_state["current_result"] = result
                                st.session_state["result_ls"] = (
                                    self.summarizers.get("Default").split_by_paragraph(result)
                                )
            with col_btn2:
                if st.button("🗑️ Clear All", use_container_width=True):
                    for key in ["current_result", "processed_result", "result_ls"]:
                        st.session_state.pop(key, None)
                    st.rerun()

        # Results
        with col2:
            st.markdown(
                '<h2 class="section-header">📄 Results</h2>', unsafe_allow_html=True
            )
            if st.session_state.get("result_ls"):
                edited_results = []
                for i, para in enumerate(st.session_state["result_ls"]):
                    height = 100 + (len(para.split()) // 50) * 100
                    edited_text = st.text_area(
                        f"Paragraph {i+1}", value=para, key=f"para_{i}", height=height
                    )
                    edited_results.append(edited_text)
                st.session_state["result_ls"] = edited_results

                if st.session_state.get("processing_time"):
                    metrics = {
                        "original_words": st.session_state["original_word_count"],
                        "summary_words": st.session_state["summary_word_count"],
                        "compression_ratio": st.session_state["compression_ratio"],
                    }
                    self.display_metrics(metrics, st.session_state["processing_time"])

                # Post-processing buttons
                col_post1, col_post2, col_post3 = st.columns(3)
                with col_post1:
                    if st.button("✨ Simplify"):
                        st.session_state["processed_result"] = (
                            self.apply_post_processing(
                                "Simplify", st.session_state["current_result"]
                            )
                        )
                with col_post2:
                    if st.button("🎯 Custom Prompt"):
                        st.session_state["processed_result"] = (
                            self.apply_post_processing(
                                "Manual Prompt", st.session_state["current_result"]
                            )
                        )
                with col_post3:
                    if st.button("📝 Shorten More"):
                        st.session_state["processed_result"] = (
                            self.apply_post_processing(
                                "Shorten", st.session_state["current_result"]
                            )
                        )
            else:
                st.markdown(
                    "**Result will appear here.** Generate a summary to see the output."
                )

    def run(self):
        self.render_main_interface()


if __name__ == "__main__":
    app = SummarizationApp()
    app.run()