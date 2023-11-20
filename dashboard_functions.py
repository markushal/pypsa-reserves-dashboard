import pypsa
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


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
