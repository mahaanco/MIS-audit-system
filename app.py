import streamlit as st
import pandas as pd
import plotly.express as px

from utils import read_mis_file
from yearly_analysis import YearlyAnalysis
from queries import Queries
from report_generator import ReportGenerator

st.set_page_config(
    page_title="Yearly MIS Audit System",
    layout="wide"
)

st.title("📊 Yearly MIS Audit System")

threshold = st.slider(
    "Variance Threshold %",
    1,
    100,
    10
)

uploaded_files = st.file_uploader(

    "Upload Monthly MIS Files",

    accept_multiple_files=True
)

if uploaded_files:

    monthly_data = []

    # Read all files
    for file in uploaded_files:

        df = read_mis_file(file)

        if not df.empty:

            month_name = (
                file.name
                .split(".")[0]
            )

            df["Month"] = month_name

            monthly_data.append(df)

    # Combine all months
    full_year_df = pd.concat(

        monthly_data,
        ignore_index=True
    )

    st.subheader("Combined Yearly MIS")

    st.dataframe(
        full_year_df.head(50)
    )

    # Yearly Analysis
    analysis = YearlyAnalysis(

        full_year_df,
        threshold
    )

    variance_df = analysis.analyze()

    st.subheader("Yearly Variance Analysis")

    st.dataframe(variance_df)

    # ---------------- CHARTS ---------------- #

    chart_df = variance_df[

        variance_df["Status"]
        == "High Variance"
    ]

    chart_df = chart_df.head(20)

    if not chart_df.empty:

        st.subheader("Top Variance Accounts")

        amount_chart = px.bar(

            chart_df,

            x="GL Name",
            y="Variance Amount",

            color="Status",

            text="Variance Amount",

            title="Highest Variance Accounts"
        )

        st.plotly_chart(
            amount_chart,
            use_container_width=True
        )

        trend_chart = px.line(

            full_year_df,

            x="Month",
            y=full_year_df.columns[-2],

            color="GL Name",

            title="Monthly Trend Analysis"
        )

        st.plotly_chart(
            trend_chart,
            use_container_width=True
        )

    # ---------------- QUERIES ---------------- #

    query_engine = Queries()

    queries_df = query_engine.generate(
        variance_df
    )

    st.subheader("Possible Client Queries")

    st.dataframe(queries_df)

    # ---------------- DOWNLOAD REPORT ---------------- #

    report = ReportGenerator.generate(

        variance_df,
        queries_df,
        full_year_df
    )

    st.download_button(

        label="Download Full Year Audit Report",

        data=report,

        file_name="Yearly_MIS_Audit_Report.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
