```python
import pandas as pd
from io import BytesIO

from kpi_generator import (
    KPIGenerator
)

from commentary_generator import (
    CommentaryGenerator
)


def generate_excel_report(
    processed_df,
    month_cols,
    all_results,
    all_queries
):

    output = BytesIO()

    kpi_engine = KPIGenerator()

    commentary_engine = (
        CommentaryGenerator()
    )

    latest_month = (
        month_cols[0]
    )

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        header_format = (
            workbook.add_format({

                "bold": True,

                "bg_color":
                "#D9EAD3",

                "border": 1
            })
        )

        # =====================
        # Executive Summary
        # =====================

        summary_df = pd.DataFrame({

            "Metric": [

                "Analysis Period",

                "Total Months",

                "Total GLs"
            ],

            "Value": [

                f"{month_cols[-1]} "
                f"to "
                f"{month_cols[0]}",

                len(
                    month_cols
                ),

                len(
                    processed_df
                )
            ]
        })

        summary_df.to_excel(
            writer,
            sheet_name=
            "Executive Summary",
            index=False
        )

        # =====================
        # KPI Dashboard
        # =====================

        kpi_df = (
            kpi_engine
            .generate_kpis(
                processed_df,
                latest_month
            )
        )

        kpi_df.to_excel(
            writer,
            sheet_name=
            "KPI Dashboard",
            index=False
        )

        # =====================
        # Variance Sheets
        # =====================

        for (
            month_pair,
            df
        ) in all_results.items():

            sheet_name = (
                month_pair[:31]
            )

            df.to_excel(
                writer,
                sheet_name=
                sheet_name,
                index=False
            )

            worksheet = (
                writer.sheets[
                    sheet_name
                ]
            )

            for (
                col_num,
                value
            ) in enumerate(
                df.columns.values
            ):

                worksheet.write(
                    0,
                    col_num,
                    value,
                    header_format
                )

        # =====================
        # Queries
        # =====================

        for (
            month_pair,
            query_df
        ) in all_queries.items():

            sheet_name = (
                f"Queries_"
                f"{month_pair}"
            )[:31]

            query_df.to_excel(
                writer,
                sheet_name=
                sheet_name,
                index=False
            )

        # =====================
        # Commentary
        # =====================

        if len(all_results):

            latest_variance = (
                list(
                    all_results.values()
                )[0]
            )

            commentary_df = (
                commentary_engine
                .generate_commentary(
                    latest_variance
                )
            )

            commentary_df.to_excel(
                writer,
                sheet_name=
                "Executive Commentary",
                index=False
            )

        output.seek(0)

    return output
```
