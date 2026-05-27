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

from queries import (
    QueryPrioritizer
)


# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="AI MIS Audit System",
    layout="wide"
)

st.title(
    "AI-Powered MIS Variance Analysis & Audit System"
)


# =========================================
# SIDEBAR CONFIGURATION
# =========================================

st.sidebar.header("Configuration")

threshold = st.sidebar.slider(
    "Variance Threshold %",
    min_value=5,
    max_value=100,
    value=15
)


# =========================================
# FILE UPLOAD
# =========================================

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


# =========================================
# MAIN PROCESSING
# =========================================

if uploaded_file:

    try:

        # =========================================
        # READ FILE
        # =========================================

        raw_df = read_file(
            uploaded_file
        )

        # =========================================
        # PREPROCESS MIS
        # =========================================

        processed_df, month_cols = (
            preprocess_mis(raw_df)
        )

        # =========================================
        # VALIDATION
        # =========================================

        if len(month_cols) < 2:

            st.error(
                "At least 2 months are required "
                "for variance analysis."
            )

            st.stop()

        # =========================================
        # SORT MONTHS
        # =========================================

        month_cols = sorted(month_cols)

        # =========================================
        # SUCCESS MESSAGE
        # =========================================

        st.success(
            "MIS File Processed Successfully"
        )

        # =========================================
        # SHOW DETECTED MONTHS
        # =========================================

        st.subheader(
            "Detected Months"
        )

        st.write(month_cols)

        # =========================================
        # SHOW PROCESSED DATA
        # =========================================

        with st.expander(
            "View Processed MIS Data"
        ):

            st.dataframe(
                processed_df,
                use_container_width=True
            )

        # =========================================
        # INITIALIZE ENGINES
        # =========================================

        analyzer = VarianceAnalyzer(
            threshold
        )

        query_engine = QueryPrioritizer()

        # =========================================
        # VARIANCE ANALYSIS
        # =========================================

        st.divider()

        st.header(
            "Rolling Variance Analysis"
        )

        for i in range(
            len(month_cols) - 1
        ):

            prev_month = month_cols[i]

            curr_month = month_cols[i + 1]

            # =========================================
            # CALCULATE VARIANCE
            # =========================================

            result_df = (
                analyzer.calculate_variance(
                    processed_df,
                    prev_month,
                    curr_month
                )
            )

            # =========================================
            # SORT HIGH VARIANCE FIRST
            # =========================================

            result_df = result_df.sort_values(
                by="Variance %",
                ascending=False
            )

            # =========================================
            # HEADER
            # =========================================

            st.divider()

            st.subheader(
                f"{prev_month} vs {curr_month}"
            )

            # =========================================
            # SHOW VARIANCE TABLE
            # =========================================

            st.dataframe(
                result_df,
                use_container_width=True
            )

            # =========================================
            # FILTER HIGH VARIANCE
            # =========================================

            high_variance = result_df[
                result_df["Status"]
                == "High Variance"
            ]

            # =========================================
            # CHARTS
            # =========================================

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

            # =========================================
            # AI QUERY PRIORITIZATION
            # =========================================

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
