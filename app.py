
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
    page_title="MIS Variance Analysis",
    layout="wide"
)

st.title(
    "AI-Powered MIS Variance Analysis & Audit System"
)


# =========================================
# SIDEBAR
# =========================================

st.sidebar.header(
    "Configuration"
)

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
# MAIN LOGIC
# =========================================

if uploaded_file:

    try:

        raw_df = read_file(
            uploaded_file
        )

        processed_df, month_cols = (
            preprocess_mis(raw_df)
        )

        if len(month_cols) < 2:

            st.error(
                "Minimum 2 months required."
            )

            st.stop()

        # =========================================
        # SORT MONTHS (LATEST FIRST)
        # =========================================

        month_cols = sorted(
            month_cols,
            key=lambda x: pd.to_datetime(
                x,
                format="%b-%y"
            ),
            reverse=True
        )

        # =========================================
        # PERIOD SELECTION
        # =========================================

        st.sidebar.subheader(
            "Analysis Period"
        )

        start_month = st.sidebar.selectbox(
            "From Month",
            month_cols,
            index=0
        )

        end_month = st.sidebar.selectbox(
            "To Month",
            month_cols,
            index=len(month_cols)-1
        )

        start_index = month_cols.index(
            start_month
        )

        end_index = month_cols.index(
            end_month
        )

        if start_index > end_index:

            st.error(
                "Invalid period selected."
            )

            st.stop()

        selected_months = month_cols[
            start_index:end_index + 1
        ]

        # =========================================
        # SUCCESS
        # =========================================

        st.success(
            "MIS Processed Successfully"
        )

        st.info(
            f"Analysis Period: "
            f"{selected_months[0]} "
            f"to "
            f"{selected_months[-1]}"
        )

        # =========================================
        # VIEW DATA
        # =========================================

        with st.expander(
            "View Processed MIS"
        ):

            st.dataframe(
                processed_df,
                use_container_width=True
            )

        analyzer = VarianceAnalyzer(
            threshold
        )

        query_engine = (
            QueryPrioritizer()
        )

        # =========================================
        # VARIANCE ANALYSIS
        # =========================================

        st.header(
            "Rolling Variance Analysis"
        )

        for i in range(
            len(selected_months) - 1
        ):

            current_month = (
                selected_months[i]
            )

            previous_month = (
                selected_months[i + 1]
            )

            result_df = (
                analyzer.calculate_variance(
                    processed_df,
                    previous_month,
                    current_month
                )
            )

            result_df = (
                result_df.sort_values(
                    by="Variance %",
                    ascending=False
                )
            )

            st.divider()

            st.subheader(
                f"{current_month} vs "
                f"{previous_month}"
            )

            st.dataframe(
                result_df,
                use_container_width=True
            )

            # =====================================
            # HIGH VARIANCE
            # =====================================

            high_variance = (
                result_df[
                    result_df["Status"]
                    == "High Variance"
                ]
            )

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

            # =====================================
            # AI QUERY PRIORITIZATION
            # =====================================

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
