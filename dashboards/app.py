import streamlit as st
import pandas as pd

from src.experiments.ab_test import evaluate_ab_test
from src.analysis.srm_check import check_srm
from src.analysis.segmentation import segment_lift
from src.analysis.guardrails import evaluate_guardrails
from src.decisioning.decision_engine import make_decision

st.title("Product Experimentation Engine")
st.write("FAANG-style experiment readout with SRM, guardrails, segmentation, and launch recommendation.")

df = pd.read_csv("data/simulated_experiment.csv")

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
    segmentation_df=all_segments
)

st.header("Primary Metric")
st.json(ab_results)

st.header("SRM Check")
st.json(srm_results)

st.header("Guardrails")
st.json(guardrail_results)

st.header("Segmentation Analysis")
st.subheader("By Platform")
st.dataframe(platform_seg)

st.subheader("By User Type")
st.dataframe(user_type_seg)

st.subheader("By Country")
st.dataframe(country_seg)

st.header("Launch Recommendation")
st.success(f"Decision: {decision['decision']}")
st.write(decision["reason"])
