import streamlit as st
import pandas as pd
import plotly.express as px
from utils import (
    read_file,
    preprocess_mis,
)
from variance_analysis import VarianceAnalyzer
from queries import generate_client_queries
from report_generator import generate_excel_report


st.set_page_config(
    page_title="AI MIS Variance Analysis System",
    layout="wide"
)

st.title("AI-Powered MIS Variance Analysis & Audit System")

st.sidebar.header("Configuration")

threshold = st.sidebar.slider(
    "High Variance Threshold (%)",
    min_value=5,
    max_value=100,
    value=20,
)

uploaded_files = st.file_uploader(
    "Upload MIS Files",
    type=["xlsx", "xls", "xlsb", "csv", "txt", "ods"],
    accept_multiple_files=True
)

if uploaded_files:

    all_month_data = {}

    for file in uploaded_files:

        try:

            raw_df = read_file(file)

            processed_df = preprocess_mis(raw_df)

            month_name = file.name.split(".")[0]

            all_month_data[month_name] = processed_df

            st.success(f"{file.name} processed successfully.")

        except Exception as e:

            st.error(f"Error processing {file.name}: {e}")

    sorted_months = list(all_month_data.keys())

    if len(sorted_months) < 2:

        st.warning("Upload at least 2 files.")

    else:

        analyzer = VarianceAnalyzer(threshold)

        all_results = {}
        all_queries = {}

        for i in range(len(sorted_months) - 1):

            prev_month = sorted_months[i]
            curr_month = sorted_months[i + 1]

            prev_df = all_month_data[prev_month]
            curr_df = all_month_data[curr_month]

            result_df = analyzer.calculate_variance(
                prev_df,
                curr_df,
                prev_month,
                curr_month
            )

            all_results[
                f"{prev_month}_vs_{curr_month}"
            ] = result_df

            query_df = generate_client_queries(
                result_df,
                prev_month,
                curr_month
            )

            all_queries[
                f"{prev_month}_vs_{curr_month}"
            ] = query_df

        st.header("Variance Analysis Dashboard")

        for month_pair, df in all_results.items():

            st.subheader(month_pair)

            st.dataframe(df, use_container_width=True)

            high_variance = df[
                df["Variance Type"] == "High Variance"
            ]

            col1, col2 = st.columns(2)

            with col1:

                fig1 = px.bar(
                    high_variance.head(15),
                    x="GL",
                    y="Variance Amount",
                    title="Top 15 Variance Amount"
                )

                st.plotly_chart(
                    fig1,
                    use_container_width=True
                )

            with col2:

                fig2 = px.bar(
                    high_variance.head(15),
                    x="GL",
                    y="Variance %",
                    title="Top 15 Variance %"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

            st.subheader("Client Queries")

            st.dataframe(
                all_queries[month_pair],
                use_container_width=True
            )

        report_file = generate_excel_report(
            all_results,
            all_queries
        )

        st.download_button(
            label="Download Audit Report",
            data=report_file,
            file_name="MIS_Variance_Audit_Report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )
