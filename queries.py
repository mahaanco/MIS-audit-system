import pandas as pd

class Queries:

    def generate(
        self,
        variance_df
    ):

        high_variance = variance_df[

            variance_df["Status"]
            == "High Variance"
        ]

        queries = []

        for _, row in high_variance.iterrows():

            query = (

                f"Why did "
                f"'{row['GL Name']}' "
                f"show yearly fluctuation of "
                f"{round(row['Variance %'],2)}% ?"
            )

            queries.append(query)

        return pd.DataFrame({

            "Possible Client Query": queries
        })
