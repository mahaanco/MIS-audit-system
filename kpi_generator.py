```python
import pandas as pd


class KPIGenerator:

    def generate_kpis(
        self,
        processed_df,
        latest_month
    ):

        total_value = (
            processed_df[
                latest_month
            ].sum()
        )

        positive_value = (
            processed_df[
                processed_df[
                    latest_month
                ] > 0
            ][latest_month]
            .sum()
        )

        negative_value = (
            processed_df[
                processed_df[
                    latest_month
                ] < 0
            ][latest_month]
            .sum()
        )

        kpi_df = pd.DataFrame({

            "KPI": [

                "Total Balance",

                "Positive Balance",

                "Negative Balance",

                "Total GLs"
            ],

            "Value": [

                round(
                    total_value,
                    2
                ),

                round(
                    positive_value,
                    2
                ),

                round(
                    negative_value,
                    2
                ),

                len(
                    processed_df
                )
            ]
        })

        return kpi_df
```
