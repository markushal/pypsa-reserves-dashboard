# -*- coding: utf-8 -*-
"""Entry point for streamlit app."""
import streamlit as st

from content.sidebar import create_sidebar
from content.tab_about import create_tab_about
from content.tab_methodology import create_tab_methodology
from content.tab_results import create_tab_results

title = "PyPSA reserves dashboard"
# app layout:
st.set_page_config(page_title=title, layout="wide")
st.title(title)

page = st.navigation(
    [
        st.Page(create_tab_results, title="Dashboard", url_path="dashboard"),
        st.Page(create_tab_methodology, title="Methodology", url_path="methodology"),
        st.Page(create_tab_about, title="About", url_path="about"),
    ],
    position="sidebar",
)

# create sidebar:
create_sidebar()

page.run()
