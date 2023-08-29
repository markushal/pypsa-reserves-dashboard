import streamlit as st
import pandas as pd
import plotly.express as px
import dashboard_functions as db
from PIL import Image


st.set_page_config(layout="wide")
st.title("Balancing power in PyPSA")
tab1, tab2 = st.tabs(["Results", "Help"])

# settings:
settings = db.create_sidebar()

# create network:
n = db.create_network(settings)

# add balancing constraints:
db.add_balancing_constraints(n, settings["contingency"])

# solve model:
n.optimize.solve_model(solver="gurobi", assign_all_duals=True)

res = db.concat_results(n)

st.divider()
st.write("Debugging output:")
st.write(n.generators)
st.write(n.storage_units)

st.write(n.storage_units["p_nom_extendable"].any())
st.code(n.model.constraints["StorageUnit-r-upper"])
st.code(n.model.constraints["StorageUnit-r-upper2"])

res_duals = pd.DataFrame(index=n.snapshots)
res_duals["p"] = n.model.dual["Bus-nodal_balance"]
res_duals["r"] = n.model.dual["reserve_margin"]

with tab1:
    col1, col2 = st.columns(2)

    # Create a figure based on the dataframe
    with col1:
        st.write("Generation (``p``) and balancing (`r`) profiles:")

        fig = px.bar(
            res[res["parameter"].isin(["p", "r"])],
            x="snapshot",
            facet_col="parameter",
            color="Generator",
            y="MW",
        )

        # add line for total load:
        total_load = n.loads_t["p_set"]
        line_trace = (
            px.line(total_load, color_discrete_sequence=["black"])
            .update_traces(name="load")
            .data[0]
        )
        fig.add_trace(line_trace, row=1, col=1)

        fig.update_layout(bargap=0, height=350)
        st.plotly_chart(fig, use_container_width=True)

        st.write("Installed capacity and average output:")
        res2 = n.generators[["p_nom", "p_nom_opt"]].copy()
        res2["p (average)"] = n.generators_t["p"].mean()
        res2["r (average)"] = n.generators_t["r"].mean()
        res2 = res2.drop("p_nom", axis=1)
        fig = px.bar(res2, barmode="group", height=350)
        fig.update_yaxes(title_text="MW")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("Generation and balancing profiles per generator:")
        fig = px.bar(
            res[(res["parameter"].isin(["p", "r"]))],
            x="snapshot",
            color="parameter",
            facet_row="Generator",
            y="MW",
            height=700,
        )

        # Create a list to store line plot traces
        line_traces = []
        # Iterate through generators and create line plot traces
        for g in res["Generator"].unique():
            line_data = res[(res["parameter"] == "p_max") & (res["Generator"] == g)]

            line_trace = px.line(
                line_data,
                x="snapshot",
                y="MW",
                color_discrete_sequence=["black"],
            ).update_traces(
                line=dict(color="black"), name="p_max"
            )  # Customize line color as needed

            line_traces.append(line_trace.data[0])

        # Reverse the order of line plot traces
        line_traces.reverse()

        # Combine bar facet plot with line plot traces
        for i, trace in enumerate(line_traces):
            fig.add_trace(trace, row=i + 1, col=1)
        st.plotly_chart(fig, use_container_width=True)

        # prices plot:
        res_storage = pd.concat(
            [
                n.storage_units_t["state_of_charge"],
                n.storage_units_t["p"],
                n.storage_units_t["r"],
            ],
            axis=1,
            ignore_index=True,
        )
        res_storage.columns = ["state_of_charge", "p", "r"]
        exp_storage = st.expander("Storage details:")
        with exp_storage:
            fig = px.line(res_storage, markers=True)
            st.plotly_chart(fig, use_container_width=True)

        exp_prices = st.expander("Prices")
        with exp_prices:
            fig = px.line(res_duals)
            st.plotly_chart(fig, use_container_width=True)

    st.write("Aggregate statistics:")
    st.dataframe(n.statistics().style.format("{:.2f}"))


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
