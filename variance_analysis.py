import pandas as pd
import numpy as np

class VarianceAnalysis::

    def __init__(
        self,
        full_year_df,
        threshold
    ):

        self.df = full_year_df
        self.threshold = threshold

    def analyze(self):

        amount_col = self.df.columns[-2]

        # Clean amount
        self.df[amount_col] = (

            self.df[amount_col]
            .astype(str)
            .str.replace(
                r"[^\d\.-]",
                "",
                regex=True
            )
        )

        self.df[amount_col] = pd.to_numeric(

            self.df[amount_col],
            errors="coerce"

        ).fillna(0)

        # Remove invalid rows
        self.df = self.df[

            self.df["GL Name"]
            .notna()
        ]

        # Group by GL
        summary = self.df.groupby(

            "GL Name"

        )[amount_col].agg(

            ["min", "max", "mean", "sum"]

        ).reset_index()

        summary["Variance Amount"] = (

            summary["max"]
            - summary["min"]
        )

        summary["Variance %"] = np.where(

            summary["mean"] == 0,

            0,

            (
                summary["Variance Amount"]
                / abs(summary["mean"])
            ) * 100
        )

        summary["Status"] = np.where(

            abs(summary["Variance %"])
            > self.threshold,

            "High Variance",

            "Normal"
        )

        summary = summary.rename(columns={

            "sum": "Year Total",
            "mean": "Average Monthly Value",
            "min": "Minimum",
            "max": "Maximum"
        })

        return summary
