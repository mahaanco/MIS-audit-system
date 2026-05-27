import pandas as pd
import numpy as np


class VarianceAnalyzer:

    def __init__(self, threshold=20):

        self.threshold = threshold

    def calculate_variance(self, prev_df, curr_df, prev_month, curr_month):

        merged = pd.merge(
            prev_df,
            curr_df,
            on="GL",
            how="outer",
            suffixes=("_prev", "_curr")
        ).fillna(0)

        merged.rename(
            columns={
                "Amount_prev": prev_month,
                "Amount_curr": curr_month,
            },
            inplace=True,
        )

        merged["Variance Amount"] = (
            merged[curr_month] - merged[prev_month]
        )

        merged["Variance %"] = np.where(
            (merged[prev_month] == 0) &
            (merged[curr_month] == 0),
            0,

            np.where(
                merged[prev_month] == 0,
                np.nan,

                (
                    (merged[curr_month] - merged[prev_month])
                    / merged[prev_month]
                ) * 100
            )
        )

        merged["Variance Type"] = np.where(
            merged["Variance %"].abs() >= self.threshold,
            "High Variance",
            "Normal"
        )

        return merged
