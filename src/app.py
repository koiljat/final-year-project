import streamlit as st
import time
from typing import Optional, Dict, Any
from llm.postprocessing import PostProcessor
from llm.summarize.summarizer import (
    RAGSummarizer,
    ZeroShotSummarizer,
    MapReduceSummarizer,
)
import traceback
import PyPDF2
import os


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
        .api-key-container {background-color:#fff3cd;border:1px solid #ffeaa7;border-radius:8px;padding:1rem;margin:1rem 0;}
        .api-key-warning {color:#856404;font-weight:500;}
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
            "provider": "openai",
            "creativity_level": 0.7,
            "complexity_level": 3,
            "api_key_validated": False,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # ---------------------------
    # API Key Management
    # ---------------------------
    def check_api_key(self, provider: str) -> bool:
        """Check if API key exists in environment variables"""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "perplexity": "PERPLEXITY_API_KEY",
            "gemini": "GEMINI_API_KEY"
        }
        
        env_key = key_mapping.get(provider)
        if env_key:
            return bool(os.getenv(env_key))
        return False

    def set_api_key(self, provider: str, api_key: str):
        """Set API key in environment variables"""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "perplexity": "PERPLEXITY_API_KEY",
            "gemini": "GEMINI_API_KEY"
        }
        
        env_key = key_mapping.get(provider)
        if env_key and api_key.strip():
            os.environ[env_key] = api_key.strip()
            return True
        return False

    def render_api_key_input(self, provider: str) -> bool:
        """Render API key input interface and return whether key is valid"""
        st.markdown(
            '<div class="api-key-container">'
            '<p class="api-key-warning">⚠️ API Key Required</p>'
            f'<p>Please enter your {provider.title()} API key to continue.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        
        api_key = st.text_input(
            f"Enter your {provider.title()} API Key:",
            type="password",
            key=f"api_key_input_{provider}",
            help=f"Your {provider.title()} API key will be stored securely for this session only."
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"Validate Key", key=f"validate_{provider}"):
                if api_key.strip():
                    if self.set_api_key(provider, api_key):
                        st.session_state["api_key_validated"] = True
                        st.success(f"✅ {provider.title()} API key validated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid API key format")
                else:
                    st.warning("Please enter your API key")
        
        return False

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
        with col1:
            st.metric("Original Words", f"{metrics['original_words']:,}")
        with col2:
            st.metric("Summary Words", f"{metrics['summary_words']:,}")
        with col3:
            st.metric("Compression", f"{metrics['compression_ratio']}%")
        with col4:
            st.metric("Processing Time", f"{processing_time:.2f}s")

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
        post_processor = PostProcessor()
        post_processor.set_provider(st.session_state["provider"])

        try:
            operations = {
                "Simplify": "simplify",
                "Manual Prompt": "custom",
                "Shorten": "shorten",
            }
            mode = operations.get(operation)
            if mode:
                return post_processor.process(text, mode=mode)
            else:
                st.warning(f"Unknown operation: {operation}")
                return text
        except Exception as e:
            st.error(f"Post-processing error: {str(e)}")
            return text

    # ---------------------------
    # Sidebar
    # ---------------------------
    def render_sidebar(self):
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            
            # Provider selection
            st.session_state["provider"] = st.selectbox(
                "Select API Provider:",
                ["perplexity", "openai", "gemini"],
                index=["perplexity", "openai", "gemini"].index(
                    st.session_state.get("provider", "openai")
                ),
                on_change=lambda: st.session_state.update({"api_key_validated": False})
            )
            
            # API Key status
            current_provider = st.session_state["provider"]
            has_api_key = self.check_api_key(current_provider)
            
            if has_api_key:
                st.success(f"✅ {current_provider.title()} API key found")
                st.session_state["api_key_validated"] = True
            else:
                st.warning(f"⚠️ No {current_provider.title()} API key found")
                st.session_state["api_key_validated"] = False
            
            st.markdown("---")
            
            st.session_state["creativity_level"] = st.slider(
                "Creativity Level",
                0.1,
                1.0,
                st.session_state.get("creativity_level", 0.7),
                0.1,
            )
            st.session_state["complexity_level"] = st.slider(
                "Complexity Level", 1, 5, st.session_state.get("complexity_level", 3)
            )
            
            st.markdown("---")
            st.markdown("### 📁 Upload File")
            file = st.file_uploader(
                "Upload a text file", type=["txt", "md", "rtf", "pdf"]
            )
            if file:
                try:
                    content = ""
                    if file.type == "application/pdf":
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            content += page.extract_text() or ""
                    else:
                        content = str(file.read(), "utf-8")

                    if content.strip():
                        st.success(f"File loaded: {len(content.split())} words")
                        st.session_state["summarize_input"] = content
                        st.session_state["file_uploaded"] = True
                    else:
                        st.error("File appears to be empty or could not be read.")
                        st.session_state["file_uploaded"] = False
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    st.session_state["file_uploaded"] = False
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

        # Check if API key is available
        current_provider = st.session_state["provider"]
        has_api_key = self.check_api_key(current_provider)
        
        if not has_api_key and not st.session_state.get("api_key_validated"):
            # Show API key input if no key found
            if not self.render_api_key_input(current_provider):
                st.info("Please enter your API key to continue using the application.")
                return

        # Input Section (Top)
        st.markdown(
            '<h2 class="section-header">📝 Input</h2>', unsafe_allow_html=True
        )
        
        method = st.selectbox(
            "Select Summarization Method:",
            ["Default", "RAG", "MapReduce"],
        )

        # Use callback for text_area to handle updates properly
        summarize_input = st.text_area(
            "Enter or paste content:",
            value=st.session_state.get("summarize_input", ""),
            height=300,
            disabled=st.session_state.get("file_uploaded", False),
            key="text_input_area",
        )

        # Update session state when text changes
        if summarize_input != st.session_state.get("summarize_input", ""):
            st.session_state["summarize_input"] = summarize_input

        if summarize_input:
            st.caption(
                f"📊 Input: {len(summarize_input.split()):,} words • {len(summarize_input):,} characters"
            )

        # Actions
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            # Disable button if no API key
            button_disabled = not (has_api_key or st.session_state.get("api_key_validated"))
            
            if st.button(
                "🚀 Generate Summary", 
                use_container_width=True, 
                disabled=button_disabled
            ):
                if summarize_input and summarize_input.strip():
                    with st.spinner("Processing..."):
                        result = self.process_text(method, summarize_input)
                        if result:
                            st.session_state["current_result"] = result
                            try:
                                st.session_state["result_ls"] = (
                                    PostProcessor().split_by_paragraph(result)
                                )
                            except AttributeError:
                                paragraphs = result.split("\n\n")
                                st.session_state["result_ls"] = [
                                    p.strip() for p in paragraphs if p.strip()
                                ]
                            st.success("Summary generated successfully!")
                else:
                    st.warning("Please enter some text to summarize.")
            
            if button_disabled:
                st.caption("⚠️ API key required to generate summaries")

        with col_btn2:
            if st.button("🗑️ Clear All", use_container_width=True):
                keys_to_clear = [
                    "current_result",
                    "result_ls",
                    "summarize_input",
                    "processing_time",
                    "original_word_count",
                    "summary_word_count",
                    "compression_ratio",
                    "file_uploaded",
                ]
                for key in keys_to_clear:
                    st.session_state.pop(key, None)
                st.rerun()

        # Add some vertical spacing
        st.markdown("---")

        # Results Section (Bottom)
        st.markdown(
            '<h2 class="section-header">📄 Results</h2>', unsafe_allow_html=True
        )

        if st.session_state.get("result_ls"):
            # Toggle for display mode
            display_mode = st.radio(
                "Display Mode:",
                ["Split Paragraphs", "Full Output"],
                horizontal=True,
                key="display_mode"
            )
            
            st.markdown("---")

            # Export button at the top
            st.text("Export as .txt:")
            st.download_button(
                label="Download Summary",
                data="\n\n".join(st.session_state["result_ls"]),
                file_name=f"summary_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True,
            )

            if display_mode == "Split Paragraphs":
                # Original split paragraph display
                edited_results = []

                for i, para in enumerate(st.session_state["result_ls"]):
                    if not para:  # Skip empty paragraphs
                        continue

                    # Calculate height based on content
                    height = max(100, min(300, 100 + (len(para.split()) // 10) * 20))

                    # Text area for editing
                    edited_text = st.text_area(
                        f"Paragraph {i+1}",
                        value=para,
                        key=f"para_{i}",
                        height=height,
                    )

                    # Post-processing buttons
                    (
                        post_processing_1,
                        post_processing_2,
                        post_processing_3,
                        post_processing_4,
                        spacer,
                    ) = st.columns([1, 1, 1, 1, 20])

                    # Check if API key is available for post-processing
                    processing_disabled = not (has_api_key or st.session_state.get("api_key_validated"))

                    with post_processing_1:
                        if edited_text:
                            if st.button(
                                "✨", 
                                key=f"simplify_{i}", 
                                help="Simplify this paragraph",
                                disabled=processing_disabled
                            ):
                                processed_para = self.apply_post_processing(
                                    "Simplify", edited_text
                                )
                                if processed_para != edited_text:
                                    st.session_state["result_ls"][i] = processed_para
                                    st.rerun()

                    with post_processing_2:
                        if edited_text:
                            if st.button(
                                "📝", 
                                key=f"shorten_{i}", 
                                help="Shorten this paragraph",
                                disabled=processing_disabled
                            ):
                                processed_para = self.apply_post_processing(
                                    "Shorten", edited_text
                                )
                                if processed_para != edited_text:
                                    st.session_state["result_ls"][i] = processed_para
                                    st.rerun()

                    with post_processing_3:
                        if edited_text:
                            if st.button(
                                "🗑️", key=f"remove_{i}", help="Remove this paragraph"
                            ):
                                st.session_state["result_ls"].pop(i)
                                st.rerun()

                    with post_processing_4:
                        st.download_button(
                            label="📄",  # small icon label
                            data=st.session_state["result_ls"][
                                i
                            ],  # export this paragraph
                            file_name=f"paragraph_{i+1}.txt",
                            mime="text/plain",
                            key=f"export_{i}",
                            help="Export this paragraph as .txt",
                        )

                    edited_results.append(edited_text)

                # Update session state with edited results
                if len(edited_results) == len(st.session_state["result_ls"]):
                    st.session_state["result_ls"] = edited_results

            else:  # Full Output mode
                # Display full output in a single text area
                full_output = "\n\n".join(st.session_state["result_ls"])
                
                # Calculate height based on total content
                total_words = sum(len(para.split()) for para in st.session_state["result_ls"])
                height = max(400, min(1000, 400 + (total_words // 50) * 20))
                
                edited_full_output = st.text_area(
                    "Full Summary",
                    value=full_output,
                    key="full_output",
                    height=height,
                    help="Edit the complete summary here. Changes will be reflected when you switch back to split view."
                )
                
                # Global post-processing buttons for full output
                st.markdown("**Post-processing options:**")
                (
                    full_post_1,
                    full_post_2,
                    spacer, 
                ) = st.columns([1, 1, 10])
                
                # Check if API key is available for post-processing
                processing_disabled = not (has_api_key or st.session_state.get("api_key_validated"))
                
                with full_post_1:
                    if edited_full_output:
                        if st.button(
                            "✨", 
                            key="simplify_full", 
                            help="Simplify the entire summary",
                            disabled=processing_disabled
                        ):
                            processed_full = self.apply_post_processing(
                                "Simplify", edited_full_output
                            )
                            if processed_full != edited_full_output:
                                # Split the processed text back into paragraphs
                                st.session_state["result_ls"] = processed_full.split("\n\n")
                                st.rerun()

                with full_post_2:
                    if edited_full_output:
                        if st.button(
                            "📝", 
                            key="shorten_full", 
                            help="Shorten the entire summary",
                            disabled=processing_disabled
                        ):
                            processed_full = self.apply_post_processing(
                                "Shorten", edited_full_output
                            )
                            if processed_full != edited_full_output:
                                # Split the processed text back into paragraphs
                                st.session_state["result_ls"] = processed_full.split("\n\n")
                                st.rerun()
                
                if processing_disabled:
                    st.caption("⚠️ API key required for post-processing")
                
                # Update session state if full output was edited
                if edited_full_output != full_output:
                    # Split the edited full output back into paragraphs
                    st.session_state["result_ls"] = [
                        para.strip() for para in edited_full_output.split("\n\n") 
                        if para.strip()
                    ]

            # Display metrics if available
            if st.session_state.get("processing_time"):
                st.markdown("---")
                metrics = {
                    "original_words": st.session_state.get(
                        "original_word_count", 0
                    ),
                    "summary_words": st.session_state.get("summary_word_count", 0),
                    "compression_ratio": st.session_state.get(
                        "compression_ratio", 0
                    ),
                }
                self.display_metrics(metrics, st.session_state["processing_time"])

        else:
            st.info(
                "**Results will appear here.** Generate a summary to see the output."
            )

    def run(self):
        try:
            self.render_main_interface()
        except Exception as e:
            st.error(f"Application error: {str(e)}")
            st.text(traceback.format_exc())


if __name__ == "__main__":
    app = SummarizationApp()
    app.run()