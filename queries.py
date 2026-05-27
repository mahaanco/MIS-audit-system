import pandas as pd


def generate_client_queries(df):

    queries = []

    high_variance = df[
        df["Status"] == "High Variance"
    ]

    for _, row in high_variance.iterrows():

        if (
            row["Previous Month"] == 0
            and row["Current Month"] > 0
        ):
            continue

        if (
            row["Previous Month"] == 0
            and row["Current Month"] == 0
        ):
            continue

        if row["Variance"] > 0:

            query = (
                f"Why did {row['GL Name']} "
                f"increase by "
                f"{row['Variance %']}%?"
            )

        else:

            query = (
                f"Why did {row['GL Name']} "
                f"decrease by "
                f"{abs(row['Variance %'])}%?"
            )

        queries.append(query)

    return pd.DataFrame({
        "AI Queries": queries
    })
