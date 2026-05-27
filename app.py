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

trend_period = st.sidebar.selectbox(
    "Trend Analysis Period",
    [
        "3 Months",
        "6 Months",
        "12 Months",
        "All Months"
    ]
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
        # SHOW MONTHS DETECTED
        # =========================================

        st.subheader(
            "Detected Months"
        )

        st.write(month_cols)

        # =========================================
        # SHOW PROCESSED MIS
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

        trend_analyzer = TrendAnalyzer()

        query_engine = QueryPrioritizer()

        # =========================================
        # TREND PERIOD LOGIC
        # =========================================

        if trend_period == "3 Months":

            trend_months = (
                month_cols[-3:]
            )

        elif trend_period == "6 Months":

            trend_months = (
                month_cols[-6:]
            )

        elif trend_period == "12 Months":

            trend_months = (
                month_cols[-12:]
            )

        else:

            trend_months = month_cols

        # =========================================
        # TREND ANALYSIS
        # =========================================

        st.divider()

        st.header(
            "Trend Analysis"
        )

        st.write(
            f"Trend Period Used: "
            f"{', '.join(trend_months)}"
        )

        trend_df = (
            trend_analyzer.calculate_trends(
                processed_df,
                trend_months
            )
        )

        # Sort by volatility
        trend_df = trend_df.sort_values(
            by="Volatility %",
            ascending=False
        )

        st.dataframe(
            trend_df,
            use_container_width=True
        )

        # =========================================
        # TREND CHART
        # =========================================

        st.subheader(
            "Top Trend Analysis"
        )

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
            # HEADER
            # =========================================

            st.divider()

            st.subheader(
                f"{prev_month} vs {curr_month}"
            )

            # =========================================
            # SORT HIGH VARIANCE FIRST
            # =========================================

            result_df = result_df.sort_values(
                by="Variance %",
                ascending=False
            )

            # =========================================
            # SHOW VARIANCE TABLE
            # =========================================

            st.dataframe(
                result_df,
                use_container_width=True
            )

            # =========================================
            # HIGH VARIANCE FILTER
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
