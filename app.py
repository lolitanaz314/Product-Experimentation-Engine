import pandas as pd
import streamlit as st

from src.design.experiment_design import plan_experiment
from src.experiments.ab_test import evaluate_ab_test
from src.analysis.srm_check import check_srm
from src.analysis.guardrails import evaluate_guardrails
from src.analysis.segmentation import segment_lift
from src.decisioning.decision_engine import make_decision

st.set_page_config(page_title="Product Experimentation Engine", layout="wide")

st.title("Product Experimentation Engine")
st.write("Experiment planning, analysis, and launch recommendation.")

df = pd.read_csv("data/simulated_experiment.csv")

plan = plan_experiment()
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
    alpha=plan["alpha"]
)

col1, col2 = st.columns(2)

with col1:
    st.header("Experiment Plan")
    st.json(plan)

with col2:
    st.header("Primary Metric")
    st.json(ab_results)

st.header("SRM Check")
st.json(srm_results)

st.header("Guardrails")
st.json(guardrail_results)

st.header("Segmentation")
seg1, seg2, seg3 = st.columns(3)

with seg1:
    st.subheader("Platform")
    st.dataframe(platform_seg, use_container_width=True)

with seg2:
    st.subheader("User Type")
    st.dataframe(user_type_seg, use_container_width=True)

with seg3:
    st.subheader("Country")
    st.dataframe(country_seg, use_container_width=True)

st.header("Launch Recommendation")
st.success(f"Decision: {decision['decision']}")
st.write(decision["reason"])
