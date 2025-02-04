# -*- coding: utf-8 -*-
"""About page content."""
from pathlib import Path

import streamlit as st


def create_tab_about():
    """Render content of about page."""
    st.markdown(
        (Path(__file__).parent.parent / "static" / "about.md").read_text(
            encoding="utf-8"
        )
    )
