# -*- coding: utf-8 -*-
"""About page content."""
from pathlib import Path

import streamlit as st


def create_tab_about():
    """Render content of about page."""
    st.markdown("This dashboard was developed as part of the IND-E project.")
    st.image(Path(__file__).parent.parent / "static" / "BMWK_Fz_2017_Web2x_en.gif")

    st.markdown(
        (Path(__file__).parent.parent / "static" / "about.md").read_text(
            encoding="utf-8"
        )
    )
