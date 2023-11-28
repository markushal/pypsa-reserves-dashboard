import streamlit as st
import pypsa
import pandas as pd
from content.functions_figures import create_figure_gen_profiles
from content.functions_figures import create_figure_capacity_and_average_output
from content.functions_figures import create_figure_gen_profiles_details
from content.functions_figures import create_figures_storage_details
from content.functions_figures import create_figure_prices


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
    exp_storage = st.expander("Storage details")
    with exp_storage:
        create_figures_storage_details(n)

    # prices profiles:
    exp_prices = st.expander("Prices")
    with exp_prices:
        create_figure_prices(n)

    st.divider()
    exp_debugging_output = st.expander("Debugging output")
    with exp_debugging_output:
        st.write(n.generators)
        st.write(n.storage_units)

        st.code(n.model.constraints["StorageUnit-r-upper"])
        st.code(n.model.constraints["StorageUnit-r-upper2"])
