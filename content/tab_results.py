# -*- coding: utf-8 -*-
"""Content of results tab."""
import pandas as pd
import pypsa
import streamlit as st

from content.functions_figures import (
    create_figure_capacity_and_average_output,
    create_figure_gen_profiles,
    create_figure_gen_profiles_details,
    create_figure_prices,
    create_figures_storage_details,
)


def create_tab_results(n: pypsa.Network, res: pd.DataFrame):
    col1, col2 = st.columns(2)

    # Create a figure based on the dataframe
    with col1:
        create_figure_gen_profiles(n, res)
        create_figure_capacity_and_average_output(n)

    with col2:
        create_figure_gen_profiles_details(res)

    # table with aggregate statistics:
    st.markdown("**Aggregate statistics**")
    st.dataframe(n.statistics().style.format("{:.2f}"))

    # storage details profiles:
    with st.expander("Storage details"):
        create_figures_storage_details(n)

    # prices profiles:
    with st.expander("Prices"):
        create_figure_prices(n)

    st.divider()
    with st.expander("Debugging output"):
        st.markdown("Generators:")
        st.write(n.generators)

        st.markdown("Storage units:")
        st.write(n.storage_units)

        st.markdown("Session state:")
        st.write(st.session_state)
