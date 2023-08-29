import streamlit as st
import pandas as pd
import plotly.express as px
import dashboard_functions as db
from PIL import Image

# app layout:
st.set_page_config(layout="wide")
st.title("PyPSA toy model")
tab1, tab2 = st.tabs(["Results", "Help"])

# create sidebar:
settings = db.create_sidebar()

# create network:
n = db.create_network(settings)

# add balancing constraints:
db.add_balancing_constraints(n, settings["contingency"])

# solve model:
n.optimize.solve_model(solver_name="highs", assign_all_duals=True)

# concatenate different profiles to one dataframe:
res = db.concat_results(n)

# create results tab:
with tab1:
    col1, col2 = st.columns(2)

    # Create a figure based on the dataframe
    with col1:
        db.create_figure_gen_profiles(n, res)
        db.create_figure_capacity_and_average_output(n)

    with col2:
        db.create_figure_gen_profiles_details(res)

    # table with aggregate statistics:
    st.write("Aggregate statistics:")
    st.dataframe(n.statistics().style.format("{:.2f}"))

    # storage details profiles:
    exp_storage = st.expander("Storage details")
    with exp_storage:
        db.create_figures_storage_details(n)

    # prices profiles:
    exp_prices = st.expander("Prices")
    with exp_prices:
        db.create_figure_prices(n)

    st.divider()
    exp_debugging_output = st.expander("Debugging output")
    with exp_debugging_output:
        st.write(n.generators)
        st.write(n.storage_units)

        st.code(n.model.constraints["StorageUnit-r-upper"])
        st.code(n.model.constraints["StorageUnit-r-upper2"])

# create help tab:
with tab2:
    st.write(
        r"""
        ### Methodology:
        We follow the approach that has been presented by Andreas Hösl et al here: https://www.youtube.com/watch?v=fmwDxNpSMM4&t=8043s

        The basic idea is that each generator needs to provide reserve capacity **symmetrically**. That means that it needs to be able to increase and decrease its output by the same amount in order to contribute to satisfy reserve requirements. This ensures that generators need to operate at partial load in order to provide reserve capacity. 

        It involves defining a new variable and some new constraints:
        - a new variable $p_{\text{reserve}}(g,t)$ that represents the reserve power provided by generator $g$ in time step $t$. 

        - One new constraint that ensures that for each time step $t$, the sum of all reserve power provided is greater or equal the required reserves: 
        $$
        \forall t: \sum_{g} p_{\text{reserve}}(g,t) \geq \text{reserve\_requirement}
        $$

        - One constraint to ensure that the reserve power a generator provides must be less or equal than the difference between its output $p$ and its nominal capacity $p_\text{nom}$, , multiplied with a scalar coefficient ``a``. This coefficient can have any value between 0 and 1 and represents the technical availability of a generator to provide balancing power. 
        $$
        \forall g, t: p_\text{reserve}(g, t) \leq a(g) p_\text{nom}(g) - p(g,t)
        $$

        - One constraint  to ensure that the balancing power a generator provides must be less or equal than its actual output ``p``, multiplied with a scalar coefficient ``b``. This coefficient can have any value between 0 and 1 and represents the technical availability of a generator to provide balancing power. 

        $$
        \forall g, t: p_\text{reserve}(g, t) \leq b(g) p(g,t)
        $$
        """
    )

    image = Image.open("diagram.png")
    st.image(image)

    st.write(
        r"""
        ### Limitations and other approaches:

        Note that this is a simplified approach that has significant limitations:
        - It does not distinguish between different categories of reserve power (primary, secondary and xx reserves). 
        - Reserves are provided symmetrical; there is no distinction between positive and negative reserves
        - The approach only takes into account the provision of balancing power, but not the actual call for balancing power

        All these issues can be taken into account in a MIP unit commitment model, albeit at much higher numerical costs. 

        Also note that reserve margin constraints have recently been added to PyPSA-EUR: https://github.com/PyPSA/pypsa-eur/blob/662492a23e4b0fe84f8d65611aad6668488aa88c/scripts/solve_network.py#L393-L472


        """
    )
