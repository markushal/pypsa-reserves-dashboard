# -*- coding: utf-8 -*-
"""Methodology page content."""
from pathlib import Path

import streamlit as st


def create_tab_methodology():
    """Render content of methodology page."""
    st.markdown((Path(__file__).parent.parent / "static" / "methods.md").read_text())
    st.image(Path(__file__).parent.parent / "static" / "diagram.png")
    st.markdown(
        (Path(__file__).parent.parent / "static" / "limitations.md").read_text()
    )
