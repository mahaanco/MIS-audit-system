import pandas as pd


class QueryPrioritizer:

    def __init__(self):

        pass

    def generate_queries(
        self,
        variance_df
    ):

        queries = []

        high_variance = variance_df[
            variance_df["Status"]
            == "High Variance"
        ]

        for _, row in high_variance.iterrows():

            previous = row["Previous Month"]

            current = row["Current Month"]

            variance = row["Variance"]

            variance_pct = row["Variance %"]

            gl = row["GL Name"]

            # Ignore new GLs
            if (
                previous == 0
                and current > 0
            ):

                continue

            # Ignore zero rows
            if (
                previous == 0
                and current == 0
            ):

                continue

            # Risk priority logic
            if abs(variance_pct) > 200:

                priority = "Critical"

            elif abs(variance_pct) > 100:

                priority = "High"

            elif abs(variance_pct) > 50:

                priority = "Medium"

            else:

                priority = "Low"

            # AI query generation
            if variance > 0:

                query = (
                    f"Why did "
                    f"{gl} increase by "
                    f"{round(variance_pct, 2)}%?"
                )

            else:

                query = (
                    f"Why did "
                    f"{gl} decrease by "
                    f"{abs(round(variance_pct, 2))}%?"
                )

            # Risk tagging
            risk_flags = []

            if "cash" in gl.lower():

                risk_flags.append(
                    "Cash Movement"
                )

            if "suspense" in gl.lower():

                risk_flags.append(
                    "Suspense Account"
                )

            if "round" in gl.lower():

                risk_flags.append(
                    "Round Entry"
                )

            if abs(variance) > 1000000:

                risk_flags.append(
                    "Material Variance"
                )

            queries.append({

                "Priority": priority,

                "GL Name": gl,

                "Variance": round(
                    variance,
                    2
                ),

                "Variance %": round(
                    variance_pct,
                    2
                ),

                "Risk Flags": ", ".join(
                    risk_flags
                ),

                "AI Query": query
            })

        queries_df = pd.DataFrame(
            queries
        )

        priority_order = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4
        }

        if not queries_df.empty:

            queries_df[
                "Priority Order"
            ] = queries_df[
                "Priority"
            ].map(priority_order)

            queries_df = queries_df.sort_values(
                by=[
                    "Priority Order",
                    "Variance %"
                ],
                ascending=[
                    True,
                    False
                ]
            )

            queries_df = queries_df.drop(
                columns=[
                    "Priority Order"
                ]
            )

        return queries_df
