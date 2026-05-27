from io import BytesIO
import pandas as pd

class ReportGenerator:

    @staticmethod
    def generate(

        variance_df,
        queries_df,
        full_year_df
    ):

        output = BytesIO()

        with pd.ExcelWriter(

            output,
            engine="openpyxl"

        ) as writer:

            variance_df.to_excel(

                writer,

                sheet_name="Yearly Variance",

                index=False
            )

            queries_df.to_excel(

                writer,

                sheet_name="Client Queries",

                index=False
            )

            full_year_df.to_excel(

                writer,

                sheet_name="Combined MIS",

                index=False
            )

        output.seek(0)

        return output
