import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    read_file,
    preprocess_mis,
)
from trend_analysis import TrendAnalyzer

from queries import QueryPrioritizer

from variance_analysis import (
    VarianceAnalyzer
)




st.set_page_config(
    page_title="MIS Variance Analysis",
    layout="wide"
)

st.title(
    "AI-Powered MIS Variance Analysis"
)

threshold = st.sidebar.slider(
    "Variance Threshold %",
    5,
    100,
    15
)

uploaded_file = st.file_uploader(
    "Upload MIS File",
    type=[
        "xlsx",
        "xls",
        "xlsb",
        "csv",
        "txt",
        "ods"
    ]
)

if uploaded_file:

    try:

        raw_df = read_file(
            uploaded_file
        )

        processed_df, month_cols = (
            preprocess_mis(raw_df)
        )

        analyzer = VarianceAnalyzer(
            threshold
        )

        for i in range(
            len(month_cols) - 1
        ):

            prev_month = month_cols[i]

            curr_month = month_cols[i + 1]

            result_df = (
                analyzer.calculate_variance(
                    processed_df,
                    prev_month,
                    curr_month
                )
            )

            st.divider()

            st.header(
                f"{prev_month} vs {curr_month}"
            )

            st.dataframe(
                result_df,
                use_container_width=True
            )

            high_variance = result_df[
                result_df["Status"]
                == "High Variance"
            ]

            col1, col2 = st.columns(2)

            with col1:

                fig1 = px.bar(
                    high_variance.head(15),
                    x="GL Name",
                    y="Variance",
                    title="Top Variance Accounts"
                )

                st.plotly_chart(
                    fig1,
                    use_container_width=True
                )

            with col2:

                fig2 = px.bar(
                    high_variance.head(15),
                    x="GL Name",
                    y="Variance %",
                    title="Top Variance %"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

            st.subheader(
                "AI Generated Queries"
            )

            queries_df = (
                generate_client_queries(
                    result_df
                )
            )

            st.dataframe(
                queries_df,
                use_container_width=True
            )

    except Exception as e:

        st.error(str(e))
