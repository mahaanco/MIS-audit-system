import pandas as pd
import numpy as np


class VarianceAnalyzer:

    def __init__(self, threshold=15):

        self.threshold = threshold

    def calculate_variance(
        self,
        df,
        prev_month,
        curr_month
    ):

        result = pd.DataFrame()

        result["GL Name"] = df["GL"]

        result["Previous Month"] = df[
            prev_month
        ]

        result["Current Month"] = df[
            curr_month
        ]

        result["Variance"] = (
            result["Current Month"]
            - result["Previous Month"]
        )

        result["Variance %"] = np.where(
            (
                result["Previous Month"] == 0
            ) &
            (
                result["Current Month"] == 0
            ),
            0,

            np.where(
                result["Previous Month"] == 0,
                np.nan,

                (
                    (
                        result["Current Month"]
                        - result["Previous Month"]
                    )
                    / result["Previous Month"]
                ) * 100
            )
        )

        result["Variance %"] = (
            result["Variance %"]
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0)
            .round(2)
        )

        result["Status"] = np.where(
            result["Variance %"].abs()
            >= self.threshold,

            "High Variance",

            "Normal"
        )

        return result
