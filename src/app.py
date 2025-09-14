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

from llm.visualize.visualizer import Visualizer
import streamlit.components.v1 as components
import re
import random


class SummarizationApp:
    def __init__(self):
        self.summarizers = {
            "Default": {
                "obj": ZeroShotSummarizer(),
                "desc": "Quick and efficient summarization",
                "icon": "⚡",
            },
            "RAG": {
                "obj": RAGSummarizer(),
                "desc": "Retrieval-augmented generation for enhanced context",
                "icon": "🧠",
            },
            "MapReduce": {
                "obj": MapReduceSummarizer(),
                "desc": "Hierarchical summarization for long documents",
                "icon": "🗂️",
            },
        }  # Add more summarization methods as needed

        self.visualizer = Visualizer(temperature=0.5)
        self.setup_page_config()
        self.initialize_session_state()

    def setup_page_config(self):
        """
        Sets up the Streamlit page configuration and applies custom CSS styles.
        """

        st.set_page_config(
            page_title="Selene Explains - AI Document Summarizer",
            page_icon="assets/images/logos/selene-logo-mini.ico",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.markdown(
            """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .main-header {
            text-align: center;
            background-clip: text;
            font-size: 3rem;
            font-weight: 700;
            color: #08acfc;
            margin-bottom: 0.5rem;
            font-family: 'Inter', sans-serif;
        }
        
        .subtitle {
            text-align: center;
            color: #08acfc;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            font-weight: 400;
            font-family: 'Inter', sans-serif;
        }
        
        .section-header {
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e9ecef;
            font-family: 'Inter', sans-serif;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .method-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            transition: all 0.3s ease;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
        }
        
        .method-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }
        
        .method-card.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        }
        
        .method-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .method-title {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.25rem;
            color: #2c3e50;
        }
        
        .method-desc {
            color: #6c757d;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        
        .input-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            border: 1px solid #e9ecef;
        }
        
        .results-section {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .metrics-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #dee2e6;
        }
        
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 0.25rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #6c757d;
            font-weight: 500;
        }
        
        .paragraph-container {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .paragraph-container:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        
        .paragraph-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .paragraph-title {
            font-weight: 600;
            color: #2c3e50;
            font-size: 1rem;
        }
        
        .paragraph-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .action-btn {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .action-btn:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
        }
        
        .action-btn.danger {
            background: #dc3545;
        }
        
        .action-btn.danger:hover {
            background: #c82333;
        }
        
        .progress-container {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e9ecef;
            text-align: center;
        }
        
        .upload-area {
            border: 2px dashed #cbd5e0;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            background: #f7fafc;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f0f4ff;
        }
        
        .upload-icon {
            font-size: 3rem;
            color: #a0aec0;
            margin-bottom: 1rem;
        }
        
        .upload-text {
            color: #4a5568;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .upload-subtext {
            color: #718096;
            font-size: 0.9rem;
        }
        
        .success-banner {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 500;
        }
        
        .warning-banner {
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 500;
        }
        
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            padding: 0.7rem 1.5rem;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .primary-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
        }
        
        .secondary-btn {
            background: #6c757d !important;
            color: white !important;
            border: none !important;
        }
        
        .stSelectbox > div > div {
            border-radius: 8px;
            border: 2px solid #e9ecef;
            font-family: 'Inter', sans-serif;
        }
        
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 2px solid #e9ecef;
            font-family: 'Inter', sans-serif;
            resize: vertical;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #2c3e50;
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.8rem;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def initialize_session_state(self):
        """Initializes default values in Streamlit's session state."""

        defaults = {
            "summarize_input": "",
            "current_result": None,
            "processed_result": None,
            "result_ls": None,
            "processing_time": None,
            "original_word_count": 0,
            "summary_word_count": 0,
            "file_uploaded": False,
            "provider": "openai",
            "temperature": 0.0,
            "selected_method": "Default",
            "processing_status": None,
            "show_advanced_settings": False,
            "max_tokens": 500,
            "top_p": 0.01,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def calculate_metrics(
        self, original_text: str, summary_text: str
    ) -> Dict[str, Any]:
        original_words = len(original_text.split())
        summary_words = len(summary_text.split())

        original_chars = len(original_text)
        summary_chars = len(summary_text)

        return {
            "original_words": original_words,
            "summary_words": summary_words,
            "original_chars": original_chars,
            "summary_chars": summary_chars,
        }

    def display_metrics(self, metrics: Dict[str, Any], processing_time: float):

        col1, col2, col3, col4, col5 = st.columns(
            5
        )  # col4 and col5 left empty for spacing / more metrics

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['original_words']:,}</div>
                    <div class="metric-label">Original Words</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['summary_words']:,}</div>
                    <div class="metric-label">Summary Words</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{processing_time:.1f}s</div>
                    <div class="metric-label">Processing Time</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    def render_method_selection(self):
        st.markdown("### 🔧 Select Summarization Method")

        cols = st.columns(3)

        for idx, (method, details) in enumerate(self.summarizers.items()):
            with cols[idx]:
                if st.button(
                    f"{details['icon']} {method}",
                    key=f"method_{method}",
                    help=details["desc"],
                    use_container_width=True,
                ):
                    st.session_state["selected_method"] = method

    def fake_progress(
        self, progress_bar, status_text, start_val, end_val, step_delay=0.05
    ):
        """Animate progress smoothly between two values."""
        for val in range(start_val, end_val + 1):
            progress_bar.progress(val)
            time.sleep(step_delay * random.uniform(0.8, 1.2))  # add jitter for realism

    def process_text(self, method: str, text: str) -> Optional[str]:
        try:
            st.session_state["processing_status"] = "processing"
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("🔄 Initializing summarization...")
            self.fake_progress(progress_bar, status_text, 0, 15)

            start = time.time()
            if method in self.summarizers:
                status_text.text(f"🧠 Running {method} summarization...")
                self.fake_progress(progress_bar, status_text, 15, 40)

                summarizer = self.summarizers[method]["obj"]
                summarizer.set_provider(st.session_state["provider"])

                if hasattr(summarizer, "set_temperature"):
                    summarizer.set_temperature(st.session_state["temperature"])

                self.fake_progress(progress_bar, status_text, 40, 75)

                result = summarizer.summarize(text)

                self.fake_progress(progress_bar, status_text, 75, 95)

                status_text.text("✅ Processing complete!")
                self.fake_progress(progress_bar, status_text, 95, 100)

            processing_time = time.time() - start
            st.session_state["processing_time"] = processing_time
            metrics = self.calculate_metrics(text, result)
            st.session_state.update(
                {
                    "original_word_count": metrics["original_words"],
                    "summary_word_count": metrics["summary_words"],
                }
            )

            # progress_bar.empty()
            # status_text.empty()
            st.session_state["processing_status"] = "complete"

            st.success(
                f"✅ Summary generated successfully in {processing_time:.2f} seconds!"
            )

            return result

        except Exception as e:
            st.session_state["processing_status"] = "error"
            st.error(f"❌ Error: {str(e)}")
            with st.expander("🔍 View Error Details"):
                st.code(traceback.format_exc())
            return None

    def apply_post_processing(self, operation: str, text: str) -> str:
        post_processor = PostProcessor()
        post_processor.set_provider(st.session_state["provider"])

        try:
            with st.spinner(f"🔄 Applying {operation.lower()}..."):
                operations = {
                    "Simplify": "simplify",
                    "Shorten": "shorten",
                    "Expand": "expand",
                    "Rephrase": "rephrase",
                }
                mode = operations.get(operation)
                if mode:
                    result = post_processor.process(text, mode=mode)
                    st.success(f"✅ {operation} applied successfully!")
                    return result
                else:
                    st.warning(f"⚠️ Unknown operation: {operation}")
                    return text
        except Exception as e:
            st.error(f"❌ Post-processing error: {str(e)}")
            return text

    def render_file_upload(self):
        st.markdown("##### 📁 Upload Document")

        col1, col2 = st.columns([2, 2])

        with col1:
            st.markdown(
                """
                <div class="upload-area">
                <div class="upload-icon">📄</div>
                <div class="upload-text">Drag and drop your file here</div>
                <div class="upload-subtext">Supported formats: TXT, MD, RTF, PDF (Max 10MB)</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                """
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
            """,
                unsafe_allow_html=True,
            )

            file = st.file_uploader(
                "Choose a file",
                type=["txt", "md", "rtf", "pdf"],
                help="Upload a document to summarize. Large files may take longer to process.",
                label_visibility="collapsed",
            )
            file_stats_html = ""
            file_warning_html = ""

            if file:
                try:
                    with st.spinner("📖 Reading file..."):
                        content = ""

                        if file.type == "application/pdf":
                            pdf_reader = PyPDF2.PdfReader(file)
                            for page in pdf_reader.pages:
                                content += page.extract_text() or ""
                        else:
                            content = str(file.read(), "utf-8")

                        st.session_state["summarize_input"] = content
                        st.session_state["file_uploaded"] = True

                except Exception as e:
                    st.session_state["file_uploaded"] = False

            else:
                st.session_state["file_uploaded"] = False

            st.markdown(file_stats_html, unsafe_allow_html=True)
            st.markdown(file_warning_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    def render_sidebar(self):
        with st.sidebar:
            st.image(
                "assets/images/logos/selene-logo-640.png", use_container_width=True
            )

            st.markdown("---")
            st.markdown("#### 🔌 API Provider")
            # TODO: Upgrade this to selection of specific models per provider
            st.session_state["provider"] = st.selectbox(
                "Select Provider:",
                ["openai", "perplexity", "gemini"],
                index=["openai", "perplexity", "gemini"].index(
                    st.session_state.get("provider", "openai")
                ),
                help="Choose your preferred AI provider",
            )

            provider_status = {
                "openai": ("🟢", "Stable"),
                "perplexity": ("🟡", "Beta"),
                "gemini": ("🟢", "Stable"),
            }
            status_color, status_text = provider_status.get(
                st.session_state["provider"], ("🔴", "Unknown")
            )
            st.caption(f"{status_color} Status: {status_text}")

            st.markdown("---")
            st.markdown("#### ⚙️ Settings")
            with st.expander(
                "Model Settings",
                expanded=st.session_state.get("show_advanced_settings", False),
            ):
                # temperature
                st.session_state["temperature"] = st.slider(
                    "🌡️ temperature",
                    0.1,
                    1.0,
                    st.session_state.get("temperature", 0.7),
                    0.1,
                    help="Controls creativity: Low=conservative, High=creative",
                )

                # max tokens
                st.session_state["max_tokens"] = st.slider(
                    "📝 Max Tokens",
                    50,
                    2000,
                    st.session_state.get("max_tokens", 500),
                    50,
                    help="Maximum length of output",
                )

                st.session_state["top_p"] = st.slider(
                    "🎯 Top-p",
                    0.0,
                    1.0,
                    st.session_state.get("top_p", 0.9),
                    0.05,
                    help="Nucleus sampling parameter",
                )

                st.session_state["frequency_penalty"] = st.slider(
                    "🔄 Frequency Penalty",
                    -2.0,
                    2.0,
                    st.session_state.get("frequency_penalty", 0.0),
                    0.1,
                    help="Reduces repetition",
                )

                st.session_state["presence_penalty"] = st.slider(
                    "🆕 Presence Penalty",
                    -2.0,
                    2.0,
                    st.session_state.get("presence_penalty", 0.0),
                    0.1,
                    help="Encourages topic diversity",
                )

            st.markdown("---")

            st.markdown("#### 📬 Contact & Support")
            st.markdown(
                """
                - 📧 Email: <a href="mailto:koiljat@u.nus.edu">koiljat@u.nus.edu</a>
                """,
                unsafe_allow_html=True,
            )

    def render_results_section(self):
        if not st.session_state.get("result_ls"):
            return

        st.markdown(
            '<h3 class="section-header">📋 Results</h3>', unsafe_allow_html=True
        )
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            display_mode = st.radio(
                "View Mode:",
                ["📝 Edit Paragraphs", "📄 Full Document"],
                horizontal=True,
                key="display_mode",
            )

        with col2:
            if st.session_state.get("processing_time"):
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                    <span style="font-size: 1rem; color: #6c757d;">⏱️ Generated in {st.session_state['processing_time']:.2f}s</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col3:
            export_text = "\n\n".join(st.session_state["result_ls"])
            st.download_button(
                "💾 Export",
                data=export_text,
                file_name=f"summary_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        st.markdown("---")

        if display_mode == "📝 Edit Paragraphs":
            self.render_paragraph_editor()
        else:
            self.render_full_document_editor()

        if st.session_state.get("processing_time"):
            st.markdown("---")
            metrics = {
                "original_words": st.session_state.get("original_word_count", 0),
                "summary_words": st.session_state.get("summary_word_count", 0),
                "compression_ratio": st.session_state.get("compression_ratio", 0),
            }
            self.display_metrics(metrics, st.session_state["processing_time"])

        st.markdown("</div>", unsafe_allow_html=True)

    def render_paragraph_editor(self):
        """Enhanced paragraph-by-paragraph editor with dropdown for post-processing actions"""
        st.markdown("### ✏️ Edit Individual Paragraphs")

        if not st.session_state["result_ls"]:
            return

        view_mode = st.toggle(
            "👁️ View paragraphs as Markdown", value=False, key="para_view_toggle"
        )

        for i, para in enumerate(st.session_state["result_ls"]):
            if not para or not para.strip():
                continue

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f'<div class="paragraph-title">📄 Paragraph {i+1}</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                word_count = len(para.split())
                st.caption(f"📊 {word_count} words")

            height = max(120, min(400, 120 + (len(para.split()) // 15) * 25))

            if view_mode:
                st.markdown(para)
                edited_text = para
            else:
                edited_text = st.text_area(
                    f"Content",
                    value=para,
                    key=f"para_{i}",
                    height=height,
                    label_visibility="collapsed",
                    help="Edit this paragraph directly",
                )

            col1, col2, col3, spacer, col4 = st.columns(
                [2, 1, 1, 6, 1]
            )  # col4 is for execute post-process action

            with col1:
                post_actions = ["Select Action", "Simplify", "Shorten", "Rephrase"]
                selected_action = st.selectbox(
                    "Post-process",
                    post_actions,
                    index=0,
                    key=f"post_action_{i}",
                    disabled=view_mode,
                    label_visibility="collapsed",
                    help="Apply post-processing to this paragraph",
                )
                if selected_action != "Select Action" and not view_mode:
                    with col4:
                        if st.button(
                            f"✔️",
                            key=f"apply_{selected_action}_{i}",
                            use_container_width=True,
                        ):
                            with st.spinner(f"{selected_action}..."):
                                processed = self.apply_post_processing(
                                    selected_action, str(edited_text)
                                )
                                if processed != edited_text:
                                    st.session_state["result_ls"][i] = processed
                                    st.success(f"✅ {selected_action} applied!")
                                    st.rerun()

            with col2:
                st.download_button(
                    "💾",
                    data=str(edited_text),
                    file_name=f"paragraph_{i+1}_{int(time.time())}.txt",
                    mime="text/plain",
                    key=f"export_{i}",
                    help="Export this paragraph",
                    use_container_width=True,
                )

            with col3:
                if st.button(
                    "🗑️",
                    key=f"remove_{i}",
                    help="Remove paragraph",
                    use_container_width=True,
                    disabled=view_mode,
                ):
                    if st.session_state.get(f"confirm_delete_{i}", False):
                        st.session_state["result_ls"].pop(i)
                        st.success("✅ Paragraph removed!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{i}"] = True
                        st.warning("⚠️ Click again to confirm deletion")

            if not view_mode and edited_text != para:
                st.session_state["result_ls"][i] = edited_text

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    def render_full_document_editor(self):
        """Enhanced full document editor"""
        st.markdown("### 📄 Edit Complete Document")

        full_text = "\n\n".join(st.session_state["result_ls"])

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Paragraphs", len(st.session_state["result_ls"]))
        with col2:
            st.metric("📝 Words", len(full_text.split()))
        with col3:
            st.metric("📏 Characters", len(full_text))
        with col4:
            estimated_read_time = max(1, len(full_text.split()) // 200)
            st.metric("⏱️ Read Time", f"{estimated_read_time} min")

        height = max(500, min(1200, 500 + (len(full_text.split()) // 50) * 30))

        view_mode = st.toggle(
            "👁️ View as Markdown", value=False, key="full_doc_view_toggle"
        )

        if view_mode:
            st.markdown(full_text)
            edited_full = full_text
        else:
            edited_full = st.text_area(
                "Document Content",
                value=full_text,
                key="full_output",
                height=height,
                help="Edit the complete document here",
                label_visibility="collapsed",
            )

        st.markdown("**Document Actions:**")
        col1, col2, col3, col4, spacer = st.columns([1, 1, 1, 1, 1])

        with col1:
            if st.button("✨ Simplify All", use_container_width=True):
                with st.spinner("Simplifying entire document..."):
                    processed = self.apply_post_processing("Simplify", edited_full)
                    if processed != edited_full:
                        st.session_state["result_ls"] = [
                            p.strip() for p in processed.split("\n\n") if p.strip()
                        ]
                        st.success("✅ Document simplified!")
                        st.rerun()

        with col2:
            if st.button("📝 Shorten All", use_container_width=True):
                with st.spinner("Shortening entire document..."):
                    processed = self.apply_post_processing("Shorten", edited_full)
                    if processed != edited_full:
                        st.session_state["result_ls"] = [
                            p.strip() for p in processed.split("\n\n") if p.strip()
                        ]
                        st.success("✅ Document shortened!")
                        st.rerun()

        with col3:
            if st.button("🔄 Rephrase All", use_container_width=True):
                with st.spinner("Rephrasing entire document..."):
                    processed = self.apply_post_processing("Rephrase", edited_full)
                    if processed != edited_full:
                        st.session_state["result_ls"] = [
                            p.strip() for p in processed.split("\n\n") if p.strip()
                        ]
                        st.success("✅ Document rephrased!")
                        st.rerun()

        with col4:
            if st.button(
                "📊 Repeat All",
                help="Regenerate with current settings",
                use_container_width=True,
            ):
                if st.session_state.get("summarize_input"):
                    with st.spinner("Re-analyzing document..."):
                        result = self.process_text(
                            st.session_state.get("selected_method", "Default"),
                            st.session_state["summarize_input"],
                        )
                        if result:
                            st.session_state["current_result"] = result
                            st.session_state["result_ls"] = [
                                p.strip() for p in result.split("\n\n") if p.strip()
                            ]
                            st.success("✅ Document re-analyzed!")
                            st.rerun()

        if edited_full != full_text:
            st.session_state["result_ls"] = [
                p.strip() for p in edited_full.split("\n\n") if p.strip()
            ]

    def render_main_interface(self):
        st.markdown(
            """
            <h1 class="main-header">Selene Explains</h1>
            <p class="subtitle">Transform lengthy documents into concise, meaningful summaries with AI-powered intelligence</p>
            """,
            unsafe_allow_html=True,
        )
        self.render_sidebar()

        self.render_method_selection()

        st.markdown("---")
        st.markdown(
            '<h3 class="section-header">📝 Input Document</h3>', unsafe_allow_html=True
        )

        self.render_file_upload()

        placeholder_text = "Paste your document content here, or upload a file."

        summarize_input = st.text_area(
            "Document Content",
            value=st.session_state.get("summarize_input", ""),
            height=300,
            disabled=st.session_state.get("file_uploaded", False),
            key="text_input_area",
            placeholder=placeholder_text,
            help="Enter the text you want to summarize, or use the file upload in the sidebar",
        )

        if summarize_input != st.session_state.get("summarize_input", ""):
            st.session_state["summarize_input"] = summarize_input

        if summarize_input:
            words = len(summarize_input.split())
            chars = len(summarize_input)
            estimated_time = max(
                5, words // 300
            )  # Rough estimate: 300 words per second

            col1, col2, col3, col4 = st.columns([0.75, 1, 1, 4])
            with col1:
                st.caption(f"📊 **{words:,}** words")
            with col2:
                st.caption(f"📏 **{chars:,}** characters")
            with col3:
                st.caption(f"⏱️ Est. **{estimated_time}s** to process")

        col1, col2 = st.columns([2, 1])

        with col1:
            generate_disabled = not (summarize_input and summarize_input.strip())
            generate_help = (
                "Enter some text first"
                if generate_disabled
                else f"Generate summary using {st.session_state.get('selected_method', 'Default')} method"
            )

            if st.button(
                f"🚀 Generate Summary ({st.session_state.get('selected_method', 'Default')})",
                disabled=generate_disabled,
                help=generate_help,
                use_container_width=True,
                type="primary",
            ):
                if summarize_input and summarize_input.strip():
                    st.session_state["processing_status"] = None

                    result = self.process_text(
                        st.session_state.get("selected_method", "Default"),
                        summarize_input,
                    )

                    if result:
                        st.session_state["current_result"] = result
                        try:
                            paragraphs = [
                                p.strip() for p in result.split("\n\n") if p.strip()
                            ]
                            if not paragraphs:  # Fallback if no double newlines
                                sentences = result.split(". ")
                                # Group sentences into paragraphs of ~3 sentences each
                                paragraphs = []
                                for i in range(0, len(sentences), 3):
                                    para = ". ".join(sentences[i : i + 3])
                                    if para and not para.endswith("."):
                                        para += "."
                                    if para:
                                        paragraphs.append(para)

                            st.session_state["result_ls"] = paragraphs
                        except Exception:
                            st.session_state["result_ls"] = [
                                result
                            ]  # Fallback to single paragraph

                        st.rerun()
                else:
                    st.warning("⚠️ Please enter some text to summarize.")

        with col2:
            if st.button(
                "🗑️ Clear All",
                help="Clear all content and results",
                use_container_width=True,
            ):
                if st.session_state.get("confirm_clear", False):
                    keys_to_clear = [
                        "current_result",
                        "result_ls",
                        "summarize_input",
                        "processing_time",
                        "original_word_count",
                        "summary_word_count",
                        "file_uploaded",
                        "processing_status",
                        "confirm_clear",
                    ]
                    for key in keys_to_clear:
                        st.session_state.pop(key, None)
                    st.success("✅ All content cleared!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state["confirm_clear"] = True
                    st.warning("⚠️ Click again to confirm")

        st.markdown("</div>", unsafe_allow_html=True)

        self.render_results_section()

        if not st.session_state.get("result_ls"):
            st.markdown("---")
            with st.expander("💡 Pro Tips", expanded=False):
                st.markdown(
                    """
                **For Best Results:**
                - 📄 **Optimal length**: 500-5000 words work best
                - 🎯 **Choose method**: Default for speed, RAG for context, MapReduce for very long docs
                - 🌡️ **Adjust temperature**: Lower for factual content, higher for creative summaries
                - 🔧 **Use post-processing**: Refine paragraphs after generation
                
                **Supported Formats:**
                - 📝 Plain text, Markdown, RTF files
                - 📄 PDF documents (text will be extracted)
                - 📋 Copy-paste from any source
                """
                )

    def run(self):
        try:
            self.render_main_interface()
        except Exception as e:
            st.error(f"❌ Application error: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())


if __name__ == "__main__":
    app = SummarizationApp()
    app.run()
