# -*- coding: utf-8 -*-
"""Sidebar."""
import pandas as pd
import streamlit as st


# Settings:
def create_sidebar():
    # Create dataframe with default generator data:
    data = {
        "p_nom": [10, 10, 10, 0],
        "marginal_cost": [1, 2, 3, 10],
        "p_nom_extendable": [False, False, False, True],
        "capital_cost": [60, 50, 40, 30],
    }
    df = pd.DataFrame(
        data,
        index=[
            "Dispatchable 1",
            "Dispatchable 2",
            "Dispatchable 3",
            "Dispatchable 4",
        ],
    )

    st.sidebar.header("Settings")
    st.sidebar.subheader("Dispatchable generators")
    st.session_state["df_dispatchable_generators"] = st.sidebar.data_editor(df)
    st.session_state["df_dispatchable_generators"]["bus"] = "bus1"
    st.session_state["df_dispatchable_generators"]["carrier"] = "Dispatchable"

    st.sidebar.subheader("Renewable generation")
    c1, c2 = st.sidebar.columns(2)

    with c2:
        st.session_state["vres_is_extendable"] = st.toggle(
            "VRES extendable",
            False,
            help=(
                "If selected, the capacity of the variable renewable energy sources "
                "(VRES) is optimized by the model."
                "Otherwise, the capacity is fixed to a user defined value."
            ),
        )
    with c1:
        if st.session_state["vres_is_extendable"]:
            st.session_state["vres_capcost"] = st.slider(
                "VRES capital cost (€/MW per year):", 0, 100, 50
            )
            st.session_state["p_nom_vres"] = 0
        else:
            st.session_state["vres_capcost"] = 0
            st.session_state["p_nom_vres"] = st.slider("VRES capacity (MW):", 0, 60, 0)

    st.sidebar.subheader("Storage")
    c1, c2 = st.sidebar.columns(2)

    with c2:
        st.session_state["storage_is_extendable"] = st.toggle(
            "Storage extendable",
            False,
            help=(
                "If selected, the capacity of the storage unit is optimized by the "
                "model."
                "Otherwise, the capacity is fixed to a user defined value."
            ),
        )
    with c1:
        if st.session_state["storage_is_extendable"]:
            st.session_state["storage_capcost"] = st.slider(
                "Storage capital cost (€/MW per year):", 0, 100, 50
            )
            st.session_state["p_nom_storage"] = 0
        else:
            st.session_state["storage_capcost"] = 0
            st.session_state["p_nom_storage"] = st.slider(
                "Storage capacity (MW):", 0, 60, 0
            )

    st.sidebar.subheader("Demand")
    st.session_state["load_max"] = st.sidebar.slider("Peak load (MW):", 1, 60, 30)

    st.sidebar.subheader("Reserve")
    st.session_state["contingency"] = st.sidebar.slider(
        "reserve requirement (MW):", 0, int(0.5 * st.session_state["load_max"]), 0
    )

    # create color mapping:
    st.session_state["colormap"] = {
        "VRES": "#68c900",
        "Dispatchable 1": "#0068c9",
        "Dispatchable 2": "#4d95d9",
        "Dispatchable 3": "#99c3e9",
        "Dispatchable 4": "#e6f0fa",
        "Storage": "#c90068",
        "p_nom_opt": "#0068c9",
        "p (average)": "#99c3e9",
        "r (average)": "#c90068",
    }

    st.session_state["category_orders"] = {
        "Generator": [
            "VRES",
            "Dispatchable 1",
            "Dispatchable 2",
            "Dispatchable 3",
            "Dispatchable 4",
            "Storage",
        ]
    }
