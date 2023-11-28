import plotly.express as px
import streamlit as st
import pandas as pd
import pypsa


def create_figure_gen_profiles(n: pypsa.Network, res: pd.DataFrame):
    if st.session_state["contingency"] > 0:
        res2 = res[res["parameter"].isin(["p", "r"])]
        st.markdown("**Generation (``p``) and balancing (`r`) profiles**")
    else:
        res2 = res[res["parameter"] == "p"]
        st.markdown("**Generation profile**")
    fig = px.bar(
        res2,
        x="snapshot",
        facet_col="parameter",
        color="Generator",
        y="MW",
        category_orders={
            "Generator": [
                "VRES",
                "Dispatchable 1",
                "Dispatchable 2",
                "Dispatchable 3",
                "Dispatchable 4",
                "Storage",
            ]
        },
        color_discrete_map=st.session_state["colormap"],
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
    return


def create_figure_capacity_and_average_output(n: pypsa.Network):
    st.markdown("**Installed capacity and average output**")
    res2 = n.generators[["p_nom", "p_nom_opt"]].copy()
    res2["p (average)"] = n.generators_t["p"].mean()
    res2["r (average)"] = n.generators_t["r"].mean()
    res2 = res2.drop("p_nom", axis=1)
    fig = px.bar(res2, barmode="group", height=350)
    fig.update_yaxes(title_text="MW")
    st.plotly_chart(fig, use_container_width=True)
    return


def create_figure_gen_profiles_details(res: pd.DataFrame):
    st.markdown("**Generation and balancing profiles per generator**")
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
    return


def create_figures_storage_details(n: pypsa.Network):
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
    fig = px.line(res_storage, markers=True)
    st.plotly_chart(fig, use_container_width=True)
    return


def create_figure_prices(n: pypsa.Network):
    res_duals = pd.DataFrame(index=n.snapshots)
    res_duals["p"] = n.model.dual["Bus-nodal_balance"]
    res_duals["r"] = n.model.dual["reserve_margin"]
    fig = px.line(res_duals)
    st.plotly_chart(fig, use_container_width=True)
    return
