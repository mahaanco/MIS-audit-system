import pandas as pd
import numpy as np


class TrendAnalyzer:

    def __init__(self):

        pass

    def calculate_trends(
        self,
        processed_df,
        month_cols
    ):

        trend_results = []

        for _, row in processed_df.iterrows():

            gl = row["GL"]

            values = []

            for month in month_cols:

                values.append(
                    row[month]
                )

            values = np.array(values)

            # Skip empty rows
            if np.all(values == 0):

                continue

            # Calculate metrics
            avg_value = np.mean(values)

            std_dev = np.std(values)

            max_value = np.max(values)

            min_value = np.min(values)

            latest_value = values[-1]

            previous_value = values[-2] \
                if len(values) > 1 else 0

            # Trend %
            if previous_value == 0:

                trend_percent = 0

            else:

                trend_percent = (
                    (
                        latest_value
                        - previous_value
                    )
                    / abs(previous_value)
                ) * 100

            # Volatility
            if avg_value == 0:

                volatility = 0

            else:

                volatility = (
                    std_dev / abs(avg_value)
                ) * 100

            # Trend classification
            if trend_percent > 20:

                trend_type = "Increasing"

            elif trend_percent < -20:

                trend_type = "Decreasing"

            else:

                trend_type = "Stable"

            # Risk classification
            if volatility > 100:

                risk_level = "High"

            elif volatility > 50:

                risk_level = "Medium"

            else:

                risk_level = "Low"

            trend_results.append({

                "GL": gl,

                "Average": round(
                    avg_value,
                    2
                ),

                "Std Dev": round(
                    std_dev,
                    2
                ),

                "Latest Value": round(
                    latest_value,
                    2
                ),

                "Trend %": round(
                    trend_percent,
                    2
                ),

                "Volatility %": round(
                    volatility,
                    2
                ),

                "Trend Type": trend_type,

                "Risk Level": risk_level
            })

        return pd.DataFrame(
            trend_results
        )
