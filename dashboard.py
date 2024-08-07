# -*- coding: utf-8 -*-
"""Entry point for streamlit app."""
import streamlit as st

from content.functions import add_balancing_constraints, concat_results, create_network
from content.sidebar import create_sidebar
from content.tab_about import create_tab_about
from content.tab_methodology import create_tab_methodology
from content.tab_results import create_tab_results

# app layout:
st.set_page_config(layout="wide")
st.title("PyPSA reserves dashboard")
t_results, t_about, t_methodology = st.tabs(["Results", "About", "Methodology"])

# create sidebar:
create_sidebar()

# create network:
n = create_network()

# add balancing constraints:
add_balancing_constraints(n, st.session_state["contingency"])

# solve model:
n.optimize.solve_model(solver_name="highs", assign_all_duals=True)

# concatenate different profiles to one dataframe:
res = concat_results(n)

# create results tab:
with t_results:
    create_tab_results(n, res)

# create help tab:
with t_methodology:
    create_tab_methodology()

with t_about:
    create_tab_about()
