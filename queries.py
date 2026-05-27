import pandas as pd


def generate_client_queries(
    df,
    prev_month,
    curr_month
):

    queries = []

    for _, row in df.iterrows():

        prev_value = row[prev_month]
        curr_value = row[curr_month]

        if prev_value == 0 and curr_value > 0:
            continue

        if prev_value == 0 and curr_value == 0:
            continue

        if pd.isna(row["Variance %"]):
            continue

        if abs(row["Variance %"]) < 20:
            continue

        if curr_value > prev_value:

            q = (
                f"Why did {row['GL']} increase by "
                f"{round(row['Variance %'], 2)}% "
                f"from {prev_month} to {curr_month}?"
            )

        else:

            q = (
                f"Why did {row['GL']} decrease by "
                f"{abs(round(row['Variance %'], 2))}% "
                f"from {prev_month} to {curr_month}?"
            )

        queries.append(q)

    return pd.DataFrame({
        "Client Query": queries
    })
