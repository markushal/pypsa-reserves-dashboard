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
    df = pd.DataFrame(data, index=["1_fix", "2_fix", "3_fix", "4_ext"])

    settings = {}
    st.sidebar.header("Settings:")
    st.sidebar.subheader("Dispatchable generators:")
    settings["df_dispatchable_generators"] = st.sidebar.data_editor(df)
    settings["df_dispatchable_generators"]["bus"] = "bus1"
    settings["df_dispatchable_generators"]["carrier"] = "Dispatchable"

    st.sidebar.subheader("Renewable generation:")
    c1, c2 = st.sidebar.columns(2)

    with c2:
        settings["vres_is_extendable"] = st.checkbox("VRES extendable", False)
    with c1:
        if settings["vres_is_extendable"]:
            settings["vres_capcost"] = st.slider(
                "VRES capital cost (€/MW per year):", 0, 100, 50
            )
            settings["p_nom_vres"] = 0
        else:
            settings["vres_capcost"] = 0
            settings["p_nom_vres"] = st.slider("VRES capacity (MW):", 0, 60, 0)

    st.sidebar.subheader("Storage:")
    c1, c2 = st.sidebar.columns(2)

    with c2:
        settings["storage_is_extendable"] = st.checkbox("Storage extendable", False)
    with c1:
        if settings["storage_is_extendable"]:
            settings["storage_capcost"] = st.slider(
                "Storage capital cost (€/MW per year):", 0, 100, 50
            )
            settings["p_nom_storage"] = 0
        else:
            settings["storage_capcost"] = 0
            settings["p_nom_storage"] = st.slider("Storage capacity (MW):", 0, 60, 0)

    st.sidebar.subheader("Demand:")
    settings["load_max"] = st.sidebar.slider("Peak load (MW):", 1, 60, 30)
    settings["contingency"] = st.sidebar.slider(
        "reserve requirement (MW):", 0, int(0.5 * settings["load_max"]), 0
    )

    return settings