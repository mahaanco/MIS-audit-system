
import pandas as pd
import numpy as np


class VarianceAnalyzer:

    def __init__(
        self,
        threshold=15
    ):

        self.threshold = threshold

    def calculate_variance(
        self,
        df,
        prev_month,
        curr_month
    ):

        result = pd.DataFrame()

        result["GL Name"] = df["GL"]

        # Dynamic month names
        result[prev_month] = df[
            prev_month
        ]

        result[curr_month] = df[
            curr_month
        ]

        # Variance Amount
        result["Variance"] = (

            result[curr_month]

            - result[prev_month]
        )

        # Variance %
        result["Variance %"] = np.where(

            (
                result[prev_month] == 0
            )

            &

            (
                result[curr_month] == 0
            ),

            0,

            np.where(

                result[prev_month] == 0,

                np.nan,

                (

                    (
                        result[curr_month]

                        - result[prev_month]
                    )

                    /

                    result[prev_month]

                ) * 100
            )
        )

        result["Variance %"] = (

            result["Variance %"]

            .replace(
                [np.inf, -np.inf],
                np.nan
            )

            .fillna(0)

            .round(2)
        )

        result["Status"] = np.where(

            result["Variance %"]

            .abs()

            >= self.threshold,

            "High Variance",

            "Normal"
        )

        # Sort biggest movements first
        result = result.sort_values(

            by="Variance %",

            ascending=False
        )

        return result

