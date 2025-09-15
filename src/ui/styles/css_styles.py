"""
CSS Styles for Streamlit Summarization App
Extracted from main application to follow separation of concerns
"""

import streamlit as st

def apply_custom_styles():
    """
    Apply all custom CSS styles to the Streamlit app.
    This function should be called once at the start of the app.
    """
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


# Main CSS styles extracted from the original application
CSS_STYLES = """
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
"""

# Additional utility functions for specific styling needs
def get_method_card_style(is_selected: bool = False) -> str:
    """
    Generate CSS class for method selection cards.
    
    Args:
        is_selected: Whether this method is currently selected
        
    Returns:
        CSS class name string
    """
    base_class = "method-card"
    return f"{base_class} selected" if is_selected else base_class

def get_button_style(button_type: str = "primary") -> str:
    """
    Generate CSS class for buttons.
    
    Args:
        button_type: Type of button (primary, secondary, danger)
        
    Returns:
        CSS class name string
    """
    button_styles = {
        "primary": "primary-btn",
        "secondary": "secondary-btn", 
        "danger": "action-btn danger"
    }
    return button_styles.get(button_type, "primary-btn")

def create_metric_html(value: str, label: str) -> str:
    """
    Create HTML for a metric display card.
    
    Args:
        value: The metric value to display
        label: The metric label
        
    Returns:
        HTML string for the metric card
    """
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def create_banner_html(message: str, banner_type: str = "success") -> str:
    """
    Create HTML for success/warning banners.
    
    Args:
        message: Message to display
        banner_type: Type of banner (success, warning)
        
    Returns:
        HTML string for the banner
    """
    banner_class = f"{banner_type}-banner"
    return f'<div class="{banner_class}">{message}</div>'