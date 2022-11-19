import matplotlib.pyplot as plt
import plotly
import shap
import streamlit as st


def make_plot():
    pass

# Visuals about location and area etc

# Feature Importance Plot

# SHAP explain single prediction


def st_shap(plot, height=None) -> None:
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    st.components.v1.html(shap_html, height=height)

# SHAP summary plot
