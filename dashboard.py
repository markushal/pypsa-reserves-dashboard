import streamlit as st
import dashboard_functions as db

from content.sidebar import create_sidebar
from content.tab_results import create_tab_results
from content.tab_methodology import create_tab_methodology

# app layout:
st.set_page_config(layout="wide")
st.title("PyPSA reserves dashboard")
t_results, t_about, t_methodology = st.tabs(["Results", "About", "Methodology"])

# create sidebar:
settings = create_sidebar()


# create network:
n = db.create_network(settings)

# add balancing constraints:
db.add_balancing_constraints(n, settings["contingency"])

# solve model:
n.optimize.solve_model(solver_name="highs", assign_all_duals=True)

# concatenate different profiles to one dataframe:
res = db.concat_results(n)

# create results tab:
with t_results:
    create_tab_results(n, res)

# create help tab:
with t_methodology:
    create_tab_methodology()
