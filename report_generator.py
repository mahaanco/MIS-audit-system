import pandas as pd
from io import BytesIO


def generate_excel_report(all_results, all_queries):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        workbook = writer.book

        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#D9EAD3",
            "border": 1
        })

        for month_pair, df in all_results.items():

            sheet_name = month_pair[:31]

            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

            worksheet = writer.sheets[sheet_name]

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            worksheet.set_column(0, len(df.columns), 20)

        for month_pair, query_df in all_queries.items():

            sheet_name = f"Queries_{month_pair}"[:31]

            query_df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

        output.seek(0)

    return output
