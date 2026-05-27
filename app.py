import streamlit as st
import pandas as pd
import plotly.express as px

from utils import read_mis_file
from variance_analysis import VarianceAnalysis
from queries import Queries
from report_generator import ReportGenerator

st.set_page_config(
    page_title="Monthly MIS Variance System",
    layout="wide"
)

st.title("📊 Monthly MIS Variance System")

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

    monthly_files = []

    # Read all uploaded files
    for file in uploaded_files:

        df = read_mis_file(file)

        if not df.empty:

            month_name = (
                file.name
                .split(".")[0]
            )

            monthly_files.append({

                "month": month_name,
                "df": df
            })

    # Sort files alphabetically
    monthly_files = sorted(

        monthly_files,

        key=lambda x: x["month"]
    )

    all_variance = []

    # Compare month by month
    for i in range(

        1,
        len(monthly_files)
    ):

        previous_month = monthly_files[i - 1]
        current_month = monthly_files[i]

        variance = VarianceAnalysis(

            previous_month["df"],
            current_month["df"],
            threshold
        )

        variance_df = variance.analyze()

        variance_df["Comparison"] = (

            previous_month["month"]
            + " vs "
            + current_month["month"]
        )

        all_variance.append(
            variance_df
        )

    # Combine all variance
    final_variance_df = pd.concat(

        all_variance,
        ignore_index=True
    )

    # ---------------- DISPLAY ---------------- #

    st.subheader(
        "Monthly Variance Analysis"
    )

    st.dataframe(
        final_variance_df
    )

    # ---------------- CHART ---------------- #

    chart_df = final_variance_df[

        final_variance_df["Status"]
        == "High Variance"
    ]

    chart_df = chart_df.head(20)

    if not chart_df.empty:

        chart = px.bar(

            chart_df,

            x="GL Name",
            y="Variance",

            color="Comparison",

            title="Monthly Variance Comparison",

            text="Variance"
        )

        st.plotly_chart(
            chart,
            use_container_width=True
        )

    # ---------------- QUERIES ---------------- #

    query_engine = Queries()

    queries_df = query_engine.generate(
        final_variance_df
    )

    st.subheader(
        "Possible Client Queries"
    )

    st.dataframe(
        queries_df
    )

    # ---------------- DOWNLOAD ---------------- #

    report = ReportGenerator.generate(

        final_variance_df,
        queries_df
    )

    st.download_button(

        label="Download MIS Variance Report",

        data=report,

        file_name="Monthly_MIS_Variance_Report.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
