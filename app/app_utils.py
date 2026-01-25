import streamlit as st

def switch_page(page_name: str):
    """Switch to a different page in the Streamlit app."""
    # Map page names to their file paths
    page_mapping = {
        "lounge": "pages/1_lounge.py",
        "assistant": "pages/2_assistant.py",
        "lab": "pages/3_lab.py",
        "faq": "pages/4_faq.py",
        "terms": "pages/5_terms.py",
    }

    page_name_lower = page_name.lower().replace("_", " ")

    if page_name_lower in page_mapping:
        st.switch_page(page_mapping[page_name_lower])
    else:
        raise ValueError(f"Could not find page {page_name}. Must be one of {list(page_mapping.keys())}")
