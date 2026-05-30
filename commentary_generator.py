```python
import pandas as pd


class CommentaryGenerator:

    def generate_commentary(
        self,
        variance_df
    ):

        commentary = []

        high_variance = variance_df[
            variance_df["Status"]
            == "High Variance"
        ]

        top_accounts = (
            high_variance
            .head(5)
        )

        for _, row in top_accounts.iterrows():

            gl = row["GL Name"]

            variance_pct = round(
                row["Variance %"],
                2
            )

            if variance_pct > 0:

                commentary.append(
                    f"{gl} increased by "
                    f"{variance_pct}%."
                )

            else:

                commentary.append(
                    f"{gl} decreased by "
                    f"{abs(variance_pct)}%."
                )

        return pd.DataFrame({

            "Executive Commentary":
            commentary
        })
```
