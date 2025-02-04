# -*- coding: utf-8 -*-
"""Methodology page content."""
from pathlib import Path

import streamlit as st


def create_tab_methodology():
    """Render content of methodology page."""
    st.markdown(
        (Path(__file__).parent.parent / "static" / "methods.md").read_text(
            encoding="utf-8"
        )
    )
    st.image(Path(__file__).parent.parent / "static" / "balancing-reserves-graph.png")
    st.markdown(
        (Path(__file__).parent.parent / "static" / "limitations.md").read_text(
            encoding="utf-8"
        )
    )
