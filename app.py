# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

# Load data
@st.cache_data
def load_data():
    bird_data = pd.read_csv("DiscoveryCenterData_After2018.csv")
    family_df = pd.read_csv("bird_species_family.csv")
    return bird_data, family_df

bird_data, family_df = load_data()

# Merge and preprocess
merged_data = bird_data.merge(family_df, on="COMMON NAME", how="left")
merged_data["OBSERVATION DATE"] = pd.to_datetime(merged_data["OBSERVATION DATE"])
merged_data["year"] = merged_data["OBSERVATION DATE"].dt.year
merged_data["month"] = merged_data["OBSERVATION DATE"].dt.month
merged_data["month_name"] = merged_data["month"].apply(lambda x: calendar.month_name[x])

# Streamlit app
st.title("Bird Species Family Diversity by Month")
selected_year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023, 2024])

filtered = merged_data[(merged_data["year"] == selected_year) & merged_data["species_family"].notna()]

if filtered.empty:
    st.warning(f"No data available for {selected_year}")
else:
    bird_lists = filtered.groupby(["month", "month_name", "species_family"])["COMMON NAME"] \
        .apply(lambda x: "<br>" + "<br>".join(sorted(x.unique()))) \
        .reset_index(name="bird_list")

    summary = filtered.groupby(["month", "month_name", "species_family"]).agg(
        unique_species=("COMMON NAME", "nunique"),
        total_observations=("OBSERVATION COUNT", "sum")
    ).reset_index()

    family_month_summary = summary.merge(bird_lists, on=["month", "month_name", "species_family"])
    family_month_summary["month_number"] = family_month_summary["month"]
    family_month_summary = family_month_summary.sort_values("month_number")

    family_month_summary["hover_text"] = (
        "<b>Family:</b> " + family_month_summary["species_family"] +
        "<br><b>Unique Species:</b> " + family_month_summary["unique_species"].astype(str) +
        "<br><b>Species:</b> " + family_month_summary["bird_list"]
    )

    fig = px.bar(
        family_month_summary,
        x="month_name",
        y="unique_species",
        color="species_family",
        custom_data=["hover_text"],
        labels={"unique_species": "Number of Unique Species", "month_name": "Month"},
        title=f"Bird Species Family Diversity by Month ({selected_year})"
    )

    fig.update_traces(hovertemplate="%{customdata[0]}")
    fig.update_layout(
        barmode="stack",
        hoverlabel_align='left',
        xaxis=dict(categoryorder='array', categoryarray=list(calendar.month_name)[1:])
    )

    st.plotly_chart(fig, use_container_width=True)
