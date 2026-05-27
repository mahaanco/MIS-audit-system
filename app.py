import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    read_file,
    preprocess_mis,
)

from variance_analysis import (
    VarianceAnalyzer
)

from trend_analysis import (
    TrendAnalyzer
)

from queries import (
    QueryPrioritizer
)


st.set_page_config(
    page_title="MIS Variance Analysis",
    layout="wide"
)

st.title(
    "AI-Powered MIS Variance Analysis & Audit System"
)

# Sidebar
st.sidebar.header("Configuration")

threshold = st.sidebar.slider(
    "Variance Threshold %",
    min_value=5,
    max_value=100,
    value=15
)

# File Upload
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

        # Read file
        raw_df = read_file(
            uploaded_file
        )

        # Preprocess MIS
        processed_df, month_cols = (
            preprocess_mis(raw_df)
        )

        # Success Message
        st.success(
            "MIS File Processed Successfully"
        )

        # Show processed MIS
        st.subheader(
            "Processed MIS Data"
        )

        st.dataframe(
            processed_df,
            use_container_width=True
        )

        # Initialize analyzers
        analyzer = VarianceAnalyzer(
            threshold
        )

        trend_analyzer = TrendAnalyzer()

        query_engine = QueryPrioritizer()

        # =========================
        # Trend Analysis
        # =========================

        st.divider()

        st.header(
            "Trend Analysis"
        )

        trend_df = (
            trend_analyzer.calculate_trends(
                processed_df,
                month_cols
            )
        )

        st.dataframe(
            trend_df,
            use_container_width=True
        )

        # Trend Chart
        trend_chart_data = (
            trend_df.head(15)
        )

        fig_trend = px.bar(
            trend_chart_data,
            x="GL",
            y="Trend %",
            color="Risk Level",
            title="Top Trend Analysis"
        )

        st.plotly_chart(
            fig_trend,
            use_container_width=True
        )

        # =========================
        # Variance Analysis
        # =========================

        for i in range(
            len(month_cols) - 1
        ):

            prev_month = month_cols[i]

            curr_month = month_cols[i + 1]

            # Variance calculation
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

            # Show variance dataframe
            st.dataframe(
                result_df,
                use_container_width=True
            )

            # Filter high variance
            high_variance = result_df[
                result_df["Status"]
                == "High Variance"
            ]

            # Charts
            col1, col2 = st.columns(2)

            with col1:

                fig1 = px.bar(
                    high_variance.head(15),
                    x="GL Name",
                    y="Variance",
                    color="Status",
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
                    color="Status",
                    title="Top Variance %"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

            # =========================
            # AI Query Prioritization
            # =========================

            st.subheader(
                "AI Query Prioritization"
            )

            queries_df = (
                query_engine.generate_queries(
                    result_df
                )
            )

            st.dataframe(
                queries_df,
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )
