import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from simulations.generate_data import simulate_experiment
from src.design.experiment_design import plan_experiment
from src.experiments.ab_test import evaluate_ab_test
from src.analysis.srm_check import check_srm
from src.analysis.guardrails import evaluate_guardrails
from src.analysis.segmentation import segment_lift
from src.decisioning.decision_engine import make_decision

st.set_page_config(page_title="Product Experimentation Engine", layout="wide")


# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------
def get_scenario_defaults(scenario_name: str):
    scenarios = {
        "Healthy win": {
            "n_users": 10000,
            "uplift": 0.035,
            "mobile_share": 0.70,
            "new_user_share": 0.40,
            "us_share": 0.60,
            "induce_srm": False,
            "mobile_guardrail_hit": False,
            "heterogeneous_effects": True,
            "seed": 42,
        },
        "Guardrail regression": {
            "n_users": 10000,
            "uplift": 0.030,
            "mobile_share": 0.75,
            "new_user_share": 0.40,
            "us_share": 0.60,
            "induce_srm": False,
            "mobile_guardrail_hit": True,
            "heterogeneous_effects": True,
            "seed": 42,
        },
        "SRM failure": {
            "n_users": 10000,
            "uplift": 0.030,
            "mobile_share": 0.70,
            "new_user_share": 0.40,
            "us_share": 0.60,
            "induce_srm": True,
            "mobile_guardrail_hit": False,
            "heterogeneous_effects": True,
            "seed": 42,
        },
        "Flat / inconclusive": {
            "n_users": 5000,
            "uplift": 0.005,
            "mobile_share": 0.70,
            "new_user_share": 0.40,
            "us_share": 0.60,
            "induce_srm": False,
            "mobile_guardrail_hit": False,
            "heterogeneous_effects": False,
            "seed": 42,
        },
        "Segment-dependent win": {
            "n_users": 12000,
            "uplift": 0.030,
            "mobile_share": 0.70,
            "new_user_share": 0.50,
            "us_share": 0.60,
            "induce_srm": False,
            "mobile_guardrail_hit": True,
            "heterogeneous_effects": True,
            "seed": 42,
        },
    }
    return scenarios[scenario_name]


def decision_banner(decision: str):
    decision_lower = decision.lower()
    if "ship" in decision_lower or "launch" in decision_lower:
        st.success(f"Recommendation: {decision}")
    elif "no" in decision_lower or "hold" in decision_lower or "do not" in decision_lower:
        st.error(f"Recommendation: {decision}")
    else:
        st.warning(f"Recommendation: {decision}")


def build_summary_table(df: pd.DataFrame):
    summary = (
        df.groupby("treatment")
        .agg(
            users=("user_id", "count"),
            conversion_rate=("conversion", "mean"),
            bounce_rate=("bounced", "mean"),
            avg_session_length=("session_length", "mean"),
        )
        .reset_index()
    )
    summary["group"] = summary["treatment"].map({0: "Control", 1: "Treatment"})
    return summary[["group", "users", "conversion_rate", "bounce_rate", "avg_session_length"]]


def plot_conversion_bar(df: pd.DataFrame):
    summary = df.groupby("treatment")["conversion"].mean().reset_index()
    summary["group"] = summary["treatment"].map({0: "Control", 1: "Treatment"})

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(summary["group"], summary["conversion"])
    ax.set_title("Conversion Rate by Group")
    ax.set_ylabel("Conversion Rate")
    ax.set_ylim(0, max(summary["conversion"].max() * 1.25, 0.05))
    st.pyplot(fig)


def plot_guardrail_bar(df: pd.DataFrame):
    summary = df.groupby("treatment").agg(
        bounce_rate=("bounced", "mean"),
        session_length=("session_length", "mean"),
    ).reset_index()
    summary["group"] = summary["treatment"].map({0: "Control", 1: "Treatment"})

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(summary["group"], summary["bounce_rate"])
    ax.set_title("Bounce Rate by Group")
    ax.set_ylabel("Bounce Rate")
    ax.set_ylim(0, max(summary["bounce_rate"].max() * 1.25, 0.05))
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(summary["group"], summary["session_length"])
    ax.set_title("Average Session Length by Group")
    ax.set_ylabel("Minutes")
    st.pyplot(fig)


def plot_segment_lift(seg_df: pd.DataFrame, title: str):
    plot_df = seg_df.copy()
    if "lift" not in plot_df.columns:
        st.info(f"No 'lift' column found for {title}.")
        return

    # Best effort column selection for x-axis
    candidate_cols = [c for c in plot_df.columns if c not in ["lift", "control_rate", "treatment_rate", "p_value"]]
    x_col = candidate_cols[0] if candidate_cols else plot_df.columns[0]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(plot_df[x_col].astype(str), plot_df["lift"])
    ax.set_title(title)
    ax.set_ylabel("Lift")
    ax.set_xlabel("")
    plt.xticks(rotation=20)
    st.pyplot(fig)


# ---------------------------------------------------
# Title
# ---------------------------------------------------
st.title("Product Experimentation Engine")
st.caption("Interactive simulation, experiment readout, and launch recommendation for PM / Product DS workflows.")


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
st.sidebar.header("Scenario")
scenario = st.sidebar.selectbox(
    "Choose a preset",
    [
        "Healthy win",
        "Guardrail regression",
        "SRM failure",
        "Flat / inconclusive",
        "Segment-dependent win",
    ],
)

defaults = get_scenario_defaults(scenario)

st.sidebar.header("Experiment Design")
experiment_name = st.sidebar.text_input("Experiment name", value="homepage_cta_test")
alpha = st.sidebar.selectbox("Alpha", [0.01, 0.05, 0.10], index=1)
power = st.sidebar.selectbox("Power", [0.8, 0.9], index=0)
mde = st.sidebar.slider("MDE (absolute)", 0.005, 0.10, 0.02, 0.005)

st.sidebar.header("Simulation Controls")
n_users = st.sidebar.slider("Total users", 1000, 50000, defaults["n_users"], 1000)
uplift = st.sidebar.slider("Treatment uplift", 0.0, 0.10, defaults["uplift"], 0.005)
mobile_share = st.sidebar.slider("Mobile share", 0.0, 1.0, defaults["mobile_share"], 0.05)
new_user_share = st.sidebar.slider("New user share", 0.0, 1.0, defaults["new_user_share"], 0.05)
us_share = st.sidebar.slider("US share", 0.0, 1.0, defaults["us_share"], 0.05)
seed = st.sidebar.number_input("Random seed", min_value=0, value=defaults["seed"], step=1)

st.sidebar.header("Failure Modes / Realism")
induce_srm = st.sidebar.checkbox("Induce SRM", value=defaults["induce_srm"])
mobile_guardrail_hit = st.sidebar.checkbox("Mobile guardrail regression", value=defaults["mobile_guardrail_hit"])
heterogeneous_effects = st.sidebar.checkbox("Heterogeneous effects", value=defaults["heterogeneous_effects"])

generate_clicked = st.sidebar.button("Generate Experiment")


# ---------------------------------------------------
# Plan
# ---------------------------------------------------
plan = plan_experiment(
    experiment_name=experiment_name,
    primary_metric="conversion",
    alpha=alpha,
    power=power,
    mde=mde,
)


# ---------------------------------------------------
# Generate data
# ---------------------------------------------------
if "df" not in st.session_state or generate_clicked or st.session_state.get("last_scenario") != scenario:
    st.session_state.df = simulate_experiment(
        n_users=n_users,
        uplift=uplift,
        seed=seed,
        mobile_share=mobile_share,
        new_user_share=new_user_share,
        us_share=us_share,
        induce_srm=induce_srm,
        mobile_guardrail_hit=mobile_guardrail_hit,
        heterogeneous_effects=heterogeneous_effects,
    )
    st.session_state.last_scenario = scenario

df = st.session_state.df


# ---------------------------------------------------
# Analysis
# ---------------------------------------------------
ab_results = evaluate_ab_test(df)
srm_results = check_srm(df)
guardrail_results = evaluate_guardrails(df)

platform_seg = segment_lift(df, "platform")
user_type_seg = segment_lift(df, "user_type")
country_seg = segment_lift(df, "country")

all_segments = pd.concat([platform_seg, user_type_seg, country_seg], ignore_index=True)

decision = make_decision(
    ab_results=ab_results,
    srm_results=srm_results,
    guardrail_results=guardrail_results,
    segmentation_df=all_segments,
    alpha=plan["alpha"],
)


# ---------------------------------------------------
# PM-facing executive summary
# ---------------------------------------------------
st.subheader("Executive Summary")
decision_banner(decision["decision"])
st.write(decision["reason"])

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Users", f"{len(df):,}")

with k2:
    st.metric("Control CVR", f"{ab_results['control_rate']:.2%}")

with k3:
    st.metric("Treatment CVR", f"{ab_results['treatment_rate']:.2%}")

with k4:
    st.metric("Lift", f"{ab_results['lift']:.2%}")


# ---------------------------------------------------
# Summary table
# ---------------------------------------------------
st.subheader("Group Performance")
summary_table = build_summary_table(df)
st.dataframe(summary_table, use_container_width=True)


# ---------------------------------------------------
# Charts
# ---------------------------------------------------
st.subheader("Primary Readout")
c1, c2 = st.columns(2)

with c1:
    plot_conversion_bar(df)

with c2:
    plot_guardrail_bar(df)


# ---------------------------------------------------
# Segment charts
# ---------------------------------------------------
st.subheader("Where Is the Effect Coming From?")
seg_col1, seg_col2, seg_col3 = st.columns(3)

with seg_col1:
    plot_segment_lift(platform_seg, "Lift by Platform")

with seg_col2:
    plot_segment_lift(user_type_seg, "Lift by User Type")

with seg_col3:
    plot_segment_lift(country_seg, "Lift by Country")


# ---------------------------------------------------
# Detailed diagnostics
# ---------------------------------------------------
st.subheader("Diagnostics")
d1, d2, d3 = st.columns(3)

with d1:
    st.markdown("**Experiment Plan**")
    st.json(plan)

with d2:
    st.markdown("**Primary Metric Result**")
    st.json(ab_results)

with d3:
    st.markdown("**SRM Check**")
    st.json(srm_results)

st.markdown("**Guardrails**")
st.json(guardrail_results)


# ---------------------------------------------------
# Segment tables
# ---------------------------------------------------
st.subheader("Segment Tables")
t1, t2, t3 = st.columns(3)

with t1:
    st.markdown("**Platform**")
    st.dataframe(platform_seg, use_container_width=True)

with t2:
    st.markdown("**User Type**")
    st.dataframe(user_type_seg, use_container_width=True)

with t3:
    st.markdown("**Country**")
    st.dataframe(country_seg, use_container_width=True)


# ---------------------------------------------------
# Raw data
# ---------------------------------------------------
with st.expander("Raw Simulated Data"):
    st.dataframe(df.head(200), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download simulated dataset",
    data=csv,
    file_name="simulated_experiment.csv",
    mime="text/csv",
)