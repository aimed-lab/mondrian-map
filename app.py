import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = Path("data/case_study/pathways_prepared_for_visualization")
DATASETS = {
    "Aggressive R1": DATA_DIR / "wikipathway_aggressive_R1_TP.csv",
    "Aggressive R2": DATA_DIR / "wikipathway_aggressive_R2_TP.csv",
    "Baseline R1": DATA_DIR / "wikipathway_baseline_R1_TP.csv",
    "Baseline R2": DATA_DIR / "wikipathway_baseline_R2_TP.csv",
    "Nonaggressive R1": DATA_DIR / "wikipathway_nonaggressive_R1_TP.csv",
    "Nonaggressive R2": DATA_DIR / "wikipathway_nonaggressive_R2_TP.csv",
}

@st.cache_data
def load_pathway_info():
    info_path = Path("data/case_study/pathway_details/annotations_with_summary.json")
    with open(info_path, "r") as f:
        return json.load(f)

@st.cache_data
def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Description"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Description", ""))
    df["Ontology"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Pathway Ontology", ""))
    df["Disease"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Disease", ""))
    return df

st.title("Mondrian Map Explorer")

pathway_info = load_pathway_info()
option = st.selectbox("Select dataset", list(DATASETS.keys()))

df = load_dataset(DATASETS[option])
df["NAME"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("NAME", x))

fig = px.scatter(
    df,
    x="x",
    y="y",
    custom_data=["NAME", "Description", "Ontology", "Disease"],
    hover_template=(
        "<b>%{customdata[0]}</b><br><br>" +
        "Description: %{customdata[1]}<br>" +
        "Ontology: %{customdata[2]}<br>" +
        "Disease: %{customdata[3]}<br>" +
        "<extra></extra>"
    ),
    color="wFC",
    color_continuous_scale="RdBu",
    height=700,
    width=800,
)
fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)
