import streamlit as st
import pandas as pd


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

    st.sidebar.header("Settings:")
    st.sidebar.subheader("Dispatchable generators:")
    st.session_state["df_dispatchable_generators"] = st.sidebar.data_editor(df)
    st.session_state["df_dispatchable_generators"]["bus"] = "bus1"
    st.session_state["df_dispatchable_generators"]["carrier"] = "Dispatchable"

    st.sidebar.subheader("Renewable generation:")
    c1, c2 = st.sidebar.columns(2)

    with c2:
        st.session_state["vres_is_extendable"] = st.toggle("VRES extendable", False)
    with c1:
        if st.session_state["vres_is_extendable"]:
            st.session_state["vres_capcost"] = st.slider(
                "VRES capital cost (€/MW per year):", 0, 100, 50
            )
            st.session_state["p_nom_vres"] = 0
        else:
            st.session_state["vres_capcost"] = 0
            st.session_state["p_nom_vres"] = st.slider("VRES capacity (MW):", 0, 60, 0)

    st.sidebar.subheader("Storage:")
    c1, c2 = st.sidebar.columns(2)

    with c2:
        st.session_state["storage_is_extendable"] = st.toggle(
            "Storage extendable", False
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

    st.sidebar.subheader("Demand:")
    st.session_state["load_max"] = st.sidebar.slider("Peak load (MW):", 1, 60, 30)
    st.session_state["contingency"] = st.sidebar.slider(
        "reserve requirement (MW):", 0, int(0.5 * st.session_state["load_max"]), 0

    # create color mapping:
    st.session_state["colormap"] = {
        "VRES": "#29b09d",
        "Dispatchable 1": "#0068c9",
        "Dispatchable 2": "#3386d4",
        "Dispatchable 3": "#66a4df",
        "Dispatchable 4": "#99c3e9",
        "Storage": "#ff2b2b",
    }
    )
