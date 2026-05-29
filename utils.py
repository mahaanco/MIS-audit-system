from datetime import datetime


def detect_month_and_drcr_columns(df):

    month_data = {}

    for col in df.columns:

        col_str = str(col).strip()

        try:

            dt = pd.to_datetime(
                col_str,
                errors="raise"
            )

            # Ignore Month Change columns
            # These are usually 1st day of month
            if dt.day == 1:
                continue

            month_name = dt.strftime(
                "%b-%y"
            )

            month_data[month_name] = {
                "amount": col
            }

        except Exception:

            col_lower = col_str.lower()

            # Debit Columns
            if (
                "debit" in col_lower
                or col_lower.endswith("dr")
            ):

                month_name = (
                    col_lower
                    .replace("debit", "")
                    .replace("dr", "")
                    .strip()
                )

                if month_name not in month_data:
                    month_data[month_name] = {}

                month_data[
                    month_name
                ]["debit"] = col

            # Credit Columns
            elif (
                "credit" in col_lower
                or col_lower.endswith("cr")
            ):

                month_name = (
                    col_lower
                    .replace("credit", "")
                    .replace("cr", "")
                    .strip()
                )

                if month_name not in month_data:
                    month_data[month_name] = {}

                month_data[
                    month_name
                ]["credit"] = col

    return month_data
