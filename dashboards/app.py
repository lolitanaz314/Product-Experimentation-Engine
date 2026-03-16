import streamlit as st
import pandas as pd
from src.experiments.ab_test import evaluate_ab_test

st.title("Product Experimentation Engine")

df = pd.read_csv("data/simulated_experiment.csv")

results = evaluate_ab_test(df)

st.write("### Experiment Results")

st.write(results)
