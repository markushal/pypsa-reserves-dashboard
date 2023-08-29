import pypsa
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


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


def create_network(settings):
    n = pypsa.Network()

    n.add("Bus", name="bus1")
    n.add("Carrier", name="Dispatchable")
    n.add("Carrier", name="VRE")
    n.add("Carrier", name="Electricity")

    # create load:
    snapshots = np.linspace(1, 48, 48)
    load_profile = np.sin(snapshots / 12 * np.pi) + 3.5
    load_profile = load_profile / load_profile.max() * settings["load_max"]

    # create snapshots:
    n.set_snapshots(snapshots)
    # effect of weightings unclear -> leave them as they are
    # n.snapshot_weightings["objective"] = 8760 / len(n.snapshots)
    # n.snapshot_weightings["stores"] = 8760 / len(n.snapshots)
    # n.snapshot_weightings["generators"] = 8760 / len(n.snapshots)
    n.add("Load", name="load1", bus="bus1", carrier="Electricity", p_set=load_profile)

    # add dispatchable generators:
    n.import_components_from_dataframe(
        settings["df_dispatchable_generators"], "Generator"
    )

    # add vres:
    p_max_pu_vres = np.sin(snapshots / 24 * np.pi) * 0.5 + 0.5
    n.add(
        "Generator",
        bus="bus1",
        name="5_vres",
        carrier="VRE",
        p_nom=settings["p_nom_vres"],
        p_max_pu=p_max_pu_vres,
        p_nom_extendable=settings["vres_is_extendable"],
        capital_cost=settings["vres_capcost"],
    )

    # add storage:
    n.add(
        "StorageUnit",
        name="6_store",
        bus="bus1",
        carrier="Electricity",
        p_nom=settings["p_nom_storage"],
        capital_cost=settings["storage_capcost"],
        p_nom_extendable=settings["storage_is_extendable"],
        cyclic_state_of_charge=True,
        max_hours=24,  # float(storage_capacity) / settings["p_nom_storage"] if settings["p_nom_storage"] > 0 else 1,
        efficiency_store=0.99,
        standing_loss=0.001,
    )

    return n


def add_balancing_constraints(
    n: pypsa.Network, contingency: float = 0
) -> pypsa.Network:
    """
    Add balancing constraints to network.

    - contingency (float): reserve requirement (MW)
    """

    # create model instance:
    n.optimize.create_model()

    # add new variable reserves:
    n.model.add_variables(
        lower=0,
        upper=np.inf,
        coords=[n.snapshots, n.generators.index],
        name="Generator-r",
    )

    n.model.add_variables(
        lower=0,
        upper=np.inf,
        coords=[n.snapshots, n.storage_units.index],
        name="StorageUnit-r",
    )

    # add constraint (reserve requirements to be met in each timestep):
    reserve_generator = n.model["Generator-r"]
    reserve_storage = n.model["StorageUnit-r"]
    summed_reserve = reserve_generator.sum("Generator") + reserve_storage.sum(
        "StorageUnit"
    )
    n.model.add_constraints(summed_reserve == contingency, name="reserve_margin")

    # add constraint (reserve must be less than diff between p and p_nom)
    gen_i = n.generators.index
    ext_i = n.generators.query("p_nom_extendable").index
    fix_i = n.generators.query("not p_nom_extendable").index
    vres_i = n.generators_t.p_max_pu.columns

    p_max_pu = pypsa.descriptors.get_switchable_as_dense(n, "Generator", "p_max_pu")
    capacity_fixed = n.generators.p_nom[fix_i]

    capacity_variable = n.model["Generator-p_nom"].rename(
        {"Generator-ext": "Generator"}
    )

    dispatch = n.model["Generator-p"]
    reserve = n.model["Generator-r"]

    lhs = dispatch + reserve - capacity_variable
    rhs = (p_max_pu[fix_i] * capacity_fixed).reindex(columns=gen_i, fill_value=0)
    n.model.add_constraints(lhs <= rhs, name="Generator-r-upper")

    # add constraint (reserve must be larger than b*p)
    n.model.add_constraints(
        reserve <= dispatch,
        name="Generator-r-lower",
    )

    n.model.add_constraints(
        reserve_storage - n.model.variables["StorageUnit-state_of_charge"] <= 0,
        name="StorageUnit-r-upper",
    )
    if n.storage_units["p_nom_extendable"].any():
        storage_capacity_variable = n.model["StorageUnit-p_nom"].rename(
            {"StorageUnit-ext": "StorageUnit"}
        )
    else:
        storage_capacity_variable = 0

    lhs = (
        n.model.variables["StorageUnit-p_store"]
        + n.model.variables["StorageUnit-p_dispatch"]
        + reserve_storage
        - storage_capacity_variable
    )

    rhs = n.storage_units.p_nom
    n.model.add_constraints(lhs <= rhs, name="StorageUnit-r-upper2")

    return


def concat_results(n):
    p_max = n.generators_t["p"].copy()
    for c in p_max.columns:
        if c in n.generators_t["p_max_pu"].columns:
            p_max[c] = n.generators_t["p_max_pu"][c] * n.generators.at[c, "p_nom_opt"]
        else:
            p_max[c] = n.generators.at[c, "p_nom_opt"]
    p = n.generators_t["p"].merge(
        n.storage_units_t["p"], left_index=True, right_index=True
    )
    p.columns.name = "Generator"

    r = n.generators_t["r"].merge(
        n.storage_units_t["r"], left_index=True, right_index=True
    )
    r.columns.name = "Generator"

    res = (
        pd.concat(
            [p, r, p_max],
            axis=1,
            keys=["p", "r", "p_max"],
            names=["parameter"],
        )
        .stack()
        .stack()
    )
    res.name = "MW"
    return res.reset_index()


def create_figure_gen_profiles(n, res):
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
    return


def create_figure_capacity_and_average_output(n):
    st.write("Installed capacity and average output:")
    res2 = n.generators[["p_nom", "p_nom_opt"]].copy()
    res2["p (average)"] = n.generators_t["p"].mean()
    res2["r (average)"] = n.generators_t["r"].mean()
    res2 = res2.drop("p_nom", axis=1)
    fig = px.bar(res2, barmode="group", height=350)
    fig.update_yaxes(title_text="MW")
    st.plotly_chart(fig, use_container_width=True)
    return


def create_figure_gen_profiles_details(res):
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
    return


def create_figures_storage_details(n):
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


def create_figure_prices(n):
    res_duals = pd.DataFrame(index=n.snapshots)
    res_duals["p"] = n.model.dual["Bus-nodal_balance"]
    res_duals["r"] = n.model.dual["reserve_margin"]
    fig = px.line(res_duals)
    st.plotly_chart(fig, use_container_width=True)
    return
