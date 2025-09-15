import streamlit as st
import time
from typing import Optional, Dict, Any
from services.summarize.summarizer import (
    RAGSummarizer,
    ZeroShotSummarizer,
    MapReduceSummarizer,
)
import traceback
import PyPDF2

from services.visualize.visualizer import Visualizer
import streamlit.components.v1 as components
import re
import random
from ui.styles.css_styles import apply_custom_styles
from config.models import DEFAULT_SESSION_STATE, get_provider_for_model
from services.summarize.summarizers_registry import SUMMARIZERS, get_summarizer
from services.postprocessing.registry import get_post_processor


class SummarizationApp:
    def __init__(self):
        self.visualizer = Visualizer(temperature=0.5)
        self.setup_page_config()
        self.initialize_session_state()
        self.model_names_mapping = {
                "gpt-5": "openai",
                "gpt-4.1": "openai",
                "gpt-4o": "openai",
                "gpt-4": "openai",
                "o4-mini": "openai",
                "gemini-2.5-flash": "gemini",
                "sonar": "perplexity"
            }

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

        apply_custom_styles()
        

    def initialize_session_state(self):
        for key, value in DEFAULT_SESSION_STATE.items():
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

        cols = st.columns(len(SUMMARIZERS))

        for idx, (method, info) in enumerate(SUMMARIZERS.items()):
            with cols[idx]:
                if st.button(f"{info.icon} {method}", help=info.desc, use_container_width=True):
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
            summarizer = get_summarizer(
                method,
                model=st.session_state["model_name"],
                temperature=st.session_state["temperature"]
            )
            summarizer.set_provider(st.session_state["provider"])

            self.fake_progress(progress_bar, status_text, 40, 75)

            # Run summarization
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

    def apply_post_processing(self, operation: str, text: str):
        try:
            processor = get_post_processor(
                operation,
                model=st.session_state.get("model_name"),
                temperature=st.session_state.get("temperature", 0.7),
            )
            return processor.process(text)
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
                "assets/images/logos/selene-logo-640.png", width="stretch"
            )

            st.markdown("---")
            st.markdown("#### 🔌 API Provider")
            st.session_state["model_name"] = st.selectbox(
                "Select Model:",
                [
                    "gpt-5",
                    "gpt-4.1",
                    "gpt-4o",
                    "gpt-4",
                    "o4-mini",
                    "gemini-2.5-flash",
                    "sonar",
                ],
                index=[
                    "gpt-5",
                    "gpt-4.1",
                    "gpt-4o",
                    "gpt-4",
                    "o4-mini",
                    "gemini-2.5-flash",
                    "sonar",
                ].index(st.session_state.get("model_name", "gpt-4o")),
                help="Choose your preferred AI Model",
            )
            
            st.session_state["provider"] = get_provider_for_model(st.session_state["model_name"])

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
                    f'<div class="paragraph-title">📄 Section {i+1}</div>',
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
                            processed = self.apply_post_processing(
                                selected_action, str(edited_text)
                            )
                            if processed != edited_text:
                                st.session_state["result_ls"][i] = processed
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
            
    def render_html_images(self):
        html_code = """'<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n  <title>How Transformers Changed the Way Machines Understand Language</title>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <style>\n    body {\n      font-family: \'Segoe UI\', Arial, sans-serif;\n      background: #f7f9fb;\n      margin: 0;\n      padding: 0;\n      color: #222;\n    }\n    .infographic-container {\n      max-width: 900px;\n      margin: 40px auto;\n      background: #fff;\n      border-radius: 18px;\n      box-shadow: 0 4px 24px rgba(0,0,0,0.08);\n      padding: 40px 30px;\n    }\n    .title {\n      text-align: center;\n      font-size: 2.2em;\n      font-weight: bold;\n      color: #3a7bd5;\n      margin-bottom: 10px;\n    }\n    .subtitle {\n      text-align: center;\n      font-size: 1.2em;\n      color: #555;\n      margin-bottom: 30px;\n    }\n    .section {\n      display: flex;\n      align-items: flex-start;\n      margin-bottom: 40px;\n      gap: 24px;\n    }\n    .section-icon {\n      flex-shrink: 0;\n      width: 64px;\n      height: 64px;\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      background: #e3ecfa;\n      border-radius: 50%;\n      font-size: 2.2em;\n      color: #3a7bd5;\n      box-shadow: 0 2px 8px rgba(58,123,213,0.08);\n    }\n    .section-content {\n      flex: 1;\n    }\n    .section-title {\n      font-size: 1.3em;\n      font-weight: bold;\n      color: #3a7bd5;\n      margin-bottom: 6px;\n    }\n    .section-desc {\n      font-size: 1.05em;\n      color: #333;\n      margin-bottom: 6px;\n    }\n    .arrow {\n      text-align: center;\n      font-size: 2.5em;\n      color: #b0b8c1;\n      margin: -20px 0 10px 0;\n    }\n    .highlight {\n      background: #e3ecfa;\n      border-radius: 6px;\n      padding: 2px 6px;\n      color: #3a7bd5;\n      font-weight: 500;\n    }\n    @media (max-width: 700px) {\n      .infographic-container { padding: 20px 5px; }\n      .section { flex-direction: column; align-items: center; gap: 10px; }\n      .section-icon { margin-bottom: 8px; }\n    }\n  </style>\n</head>\n<body>\n  <div class="infographic-container">\n    <div class="title">How Transformers Changed the Way Machines Understand Language</div>\n    <div class="subtitle">A Visual Journey from Old AI to the Age of Transformers</div>\n\n    <!-- Section 1: The Old Way -->\n    <div class="section">\n      <div class="section-icon" title="Old AI">\n        <!-- Flashlight Icon (SVG) -->\n        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">\n          <rect x="7" y="2" width="10" height="6" rx="2" fill="#3a7bd5"/>\n          <rect x="9" y="8" width="6" height="10" rx="2" fill="#b0b8c1"/>\n          <rect x="10" y="18" width="4" height="4" rx="1" fill="#3a7bd5"/>\n        </svg>\n      </div>\n      <div class="section-content">\n        <div class="section-title">The Old Way: Step-by-Step Reading</div>\n        <div class="section-desc">\n          <span class="highlight">Recurrent Neural Networks (RNNs)</span> read sentences <b>one word at a time</b>, like using a flashlight in a dark room.<br>\n          <b>Problems:</b> Slow, forgetful, and struggle with long-range connections.<br>\n          <i>Example:</i> Hard to link <span class="highlight">"cat"</span> and <span class="highlight">"sat"</span> in a long sentence.\n        </div>\n      </div>\n    </div>\n\n    <div class="arrow">&#8595;</div>\n\n    <!-- Section 2: The Breakthrough -->\n    <div class="section">\n      <div class="section-icon" title="Transformer">\n        <!-- Lightbulb Icon (SVG) -->\n        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">\n          <ellipse cx="12" cy="10" rx="7" ry="7" fill="#3a7bd5"/>\n          <rect x="9" y="17" width="6" height="3" rx="1.5" fill="#b0b8c1"/>\n          <rect x="10" y="20" width="4" height="2" rx="1" fill="#3a7bd5"/>\n        </svg>\n      </div>\n      <div class="section-content">\n        <div class="section-title">The Breakthrough: Attention Is All You Need</div>\n        <div class="section-desc">\n          <span class="highlight">Transformers</span> see the <b>whole sentence at once</b>, like turning on the lights.<br>\n          <b>Key innovation:</b> <span class="highlight">Attention mechanism</span> focuses on important words, wherever they are.<br>\n          <b>Multi-head attention:</b> Like a team of readers, each spotting different patterns.<br>\n          <b>Results:</b> Faster, smarter, and more accurate—especially in translation and understanding context.\n        </div>\n      </div>\n    </div>\n\n    <div class="arrow">&#8595;</div>\n\n    <!-- Section 3: Real-World Impact -->\n    <div class="section">\n      <div class="section-icon" title="Impact">\n        <!-- Globe/AI Icon (SVG) -->\n        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">\n          <circle cx="12" cy="12" r="10" fill="#3a7bd5"/>\n          <ellipse cx="12" cy="12" rx="6" ry="10" fill="#e3ecfa"/>\n          <ellipse cx="12" cy="12" rx="10" ry="3" fill="#b0b8c1"/>\n        </svg>\n      </div>\n      <div class="section-content">\n        <div class="section-title">Why This Matters: Everyday AI</div>\n        <div class="section-desc">\n          <b>Transformers</b> power <span class="highlight">virtual assistants</span>, <span class="highlight">real-time translators</span>, <span class="highlight">smart chatbots</span>, and more.<br>\n          <b>Parallel processing</b> means faster, more scalable AI.<br>\n          <b>Impact:</b> More human-like, helpful, and accessible AI for everyone.\n        </div>\n      </div>\n    </div>\n\n    <div class="arrow">&#8595;</div>\n\n    <!-- Section 4: The New Era -->\n    <div class="section">\n      <div class="section-icon" title="Future">\n        <!-- Rocket Icon (SVG) -->\n        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">\n          <path d="M12 2 L15 8 L12 14 L9 8 Z" fill="#3a7bd5"/>\n          <circle cx="12" cy="16" r="2" fill="#b0b8c1"/>\n          <rect x="11" y="18" width="2" height="4" rx="1" fill="#3a7bd5"/>\n        </svg>\n      </div>\n      <div class="section-content">\n        <div class="section-title">A New Era of Language AI</div>\n        <div class="section-desc">\n          <b>Transformers</b> opened the door to smarter, faster, and more human-like AI.<br>\n          <b>From research labs to your phone</b>—they’re changing how we interact with technology every day.\n        </div>\n      </div>\n    </div>\n  </div>\n</body>\n</html>'
        """

        components.html(html_code, height=800, width=800, scrolling=False)


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
