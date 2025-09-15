import streamlit as st
import streamlit.components.v1 as components

import time
from typing import Optional, Dict, Any
import traceback
import PyPDF2

from services.visualize import visualizer
from services.visualize.visualizer import Visualizer
import streamlit.components.v1 as components
import random
from ui.styles.css_styles import apply_custom_styles
from config.models import (
    DEFAULT_SESSION_STATE,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    DEFAULT_MODEL_SETTINGS,
    get_provider_for_model,
)
from services.summarize.summarizers_registry import SUMMARIZERS, get_summarizer
from services.postprocessing.registry import get_post_processor


class SummarizationApp:
    def __init__(self):
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

    def render_metric(self, col, value, label):
        col.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_method_selection(self):
        st.markdown("### 🔧 Select Summarization Method")

        cols = st.columns(len(SUMMARIZERS))

        for idx, (method, info) in enumerate(SUMMARIZERS.items()):
            with cols[idx]:
                if st.button(
                    f"{info.icon} {method}", help=info.desc, use_container_width=True
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
            summarizer = get_summarizer(
                method,
                model=st.session_state["model_name"],
                temperature=st.session_state["temperature"],
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
                temperature=st.session_state.get("temperature", 0.0),
            )
            return processor.process(text)
        except Exception as e:
            st.error(f"❌ Post-processing error: {str(e)}")
            return text
        
    def render_images_section(self, summary: str):
        visualizer = Visualizer()
        html = visualizer.visualize(summary)
        components.html(html, height=1000, scrolling=True)

        

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
            st.image("assets/images/logos/selene-logo-640.png", width="stretch")

            st.markdown("---")
            st.markdown("#### 🔌 API Provider")
            st.session_state["model_name"] = st.selectbox(
                "Select Model:",
                AVAILABLE_MODELS,
                index=AVAILABLE_MODELS.index(
                    st.session_state.get("model_name", DEFAULT_MODEL)
                ),
                help="Choose your preferred AI Model",
            )

            st.session_state["provider"] = get_provider_for_model(
                st.session_state["model_name"]
            )

            st.markdown("---")
            st.markdown("#### ⚙️ Settings")
            with st.expander(
                "Model Settings",
                expanded=st.session_state.get("show_advanced_settings", False),
            ):
                for param, default in DEFAULT_MODEL_SETTINGS.items():
                    min_val, max_val, step = {
                        "temperature": (0.1, 1.0, 0.1),
                        "max_tokens": (50, 4000, 50),
                        "top_p": (0.0, 1.0, 0.05),
                        "frequency_penalty": (-2.0, 2.0, 0.1),
                        "presence_penalty": (-2.0, 2.0, 0.1),
                    }[param]

                    st.session_state[param] = st.slider(
                        f"{param.replace('_',' ').title()}",
                        min_val,
                        max_val,
                        st.session_state.get(param, default),
                        step,
                        help=f"Adjust {param.replace('_',' ')}",
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
        
        summary_text = "\n\n".join(st.session_state["result_ls"])
        self.render_images_section(summary_text)


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
            ) 

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
