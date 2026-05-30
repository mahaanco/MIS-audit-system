import pandas as pd
import re
from datetime import datetime


def read_file(uploaded_file):

    filename = uploaded_file.name.lower()

    try:

        if filename.endswith(".xlsx"):

            df = pd.read_excel(
                uploaded_file,
                header=None,
                engine="openpyxl"
            )

        elif filename.endswith(".xls"):

            df = pd.read_excel(
                uploaded_file,
                header=None,
                engine="xlrd"
            )

        elif filename.endswith(".xlsb"):

            df = pd.read_excel(
                uploaded_file,
                header=None,
                engine="pyxlsb"
            )

        elif filename.endswith(".csv"):

            df = pd.read_csv(
                uploaded_file,
                header=None
            )

        else:

            raise Exception(
                "Unsupported file format."
            )

        return df

    except Exception as e:

        raise Exception(
            f"Error reading file: {e}"
        )


def clean_dataframe(df):

    df = df.copy()

    df = df.dropna(
        how="all"
    )

    df = df.dropna(
        axis=1,
        how="all"
    )

    df = df.fillna("")

    return df


def normalize_columns(df):

    cleaned_cols = []

    seen = {}

    for col in df.columns:

        col = str(col)

        col = col.strip().lower()

        col = col.replace(
            "\n",
            " "
        )

        col = re.sub(
            r"\s+",
            " ",
            col
        )

        if col in seen:

            seen[col] += 1

            col = (
                f"{col}_{seen[col]}"
            )

        else:

            seen[col] = 0

        cleaned_cols.append(
            col
        )

    df.columns = cleaned_cols

    return df


def clean_amount_column(series):

    return pd.to_numeric(
        series.astype(str)
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.replace(
            "(",
            "-",
            regex=False
        )
        .str.replace(
            ")",
            "",
            regex=False
        )
        .str.strip(),
        errors="coerce"
    ).fillna(0)


def is_invalid_row(gl):

    gl = str(gl).strip().lower()

    invalid_keywords = [
        "total",
        "subtotal",
        "grand total",
        "entry to be passed",
        "narration",
    ]

    if gl == "":

        return True

    if any(
        word in gl
        for word in invalid_keywords
    ):

        return True

    if re.fullmatch(
        r"[\d\.\,\-]+",
        gl
    ):

        return True

    return False


def detect_ledger_column(df):

    possible_columns = [

        "gl name",

        "ledger",

        "ledger name",

        "particulars",

        "particular",

        "account name",
    ]

    for col in df.columns:

        if (
            str(col).lower()
            in possible_columns
        ):

            return col

    raise Exception(
        "Ledger column not found."
    )



def detect_month_and_drcr_columns(df):

    import re

    month_data = {}

    for col in df.columns:

        col_str = str(col).strip()

        # =====================================
        # DATE FORMAT COLUMNS
        # Examples:
        # 31-04-2026
        # 2026-03-31
        # 30/11/2025
        # =====================================

        date_match = re.search(
            r"(\d{2})[-/](\d{2})[-/](\d{4})",
            col_str
        )

        reverse_date_match = re.search(
            r"(\d{4})[-/](\d{2})[-/](\d{2})",
            col_str
        )

        if date_match:

            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = int(date_match.group(3))

            # Ignore Month Change columns
            if day == 1:
                continue

            month_name = (
                pd.Timestamp(
                    year=year,
                    month=month,
                    day=1
                )
                .strftime("%b-%y")
            )

            month_data[month_name] = {
                "amount": col
            }

            continue

        elif reverse_date_match:

            year = int(
                reverse_date_match.group(1)
            )

            month = int(
                reverse_date_match.group(2)
            )

            day = int(
                reverse_date_match.group(3)
            )

            # Ignore Month Change columns
            if day == 1:
                continue

            month_name = (
                pd.Timestamp(
                    year=year,
                    month=month,
                    day=1
                )
                .strftime("%b-%y")
            )

            month_data[month_name] = {
                "amount": col
            }

            continue

        # =====================================
        # DR / CR FORMAT
        # =====================================

        col_lower = col_str.lower()

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



def preprocess_mis(df):

    df = clean_dataframe(
        df
    )

    # Your MIS Header Row
    header_row = 3

    df.columns = [

        str(col).strip()

        for col in df.iloc[
            header_row
        ]
    ]

    df = df[
        (header_row + 1):
    ]

    df = (
        df.reset_index(
            drop=True
        )
    )

    df = normalize_columns(
        df
    )

    ledger_col = (
        detect_ledger_column(
            df
        )
    )

    month_data = (
        detect_month_and_drcr_columns(
            df
        )
    )

    processed = (
        pd.DataFrame()
    )

    processed["GL"] = (

        df[ledger_col]

        .astype(str)

        .str.strip()
    )

    processed = processed[
        ~processed[
            "GL"
        ].apply(
            is_invalid_row
        )
    ]

    final_months = []

    for (
        month,
        cols
    ) in month_data.items():

        # DR / CR format
        if (
            "debit" in cols
            or "credit"
            in cols
        ):

            debit_values = 0

            credit_values = 0

            if (
                "debit"
                in cols
            ):

                debit_values = (
                    clean_amount_column(
                        df[
                            cols[
                                "debit"
                            ]
                        ]
                    )
                )

            if (
                "credit"
                in cols
            ):

                credit_values = (
                    clean_amount_column(
                        df[
                            cols[
                                "credit"
                            ]
                        ]
                    )
                )

            processed[
                month
            ] = (
                debit_values
                - credit_values
            )

        # Single Amount format
        elif (
            "amount"
            in cols
        ):

            processed[
                month
            ] = (
                clean_amount_column(
                    df[
                        cols[
                            "amount"
                        ]
                    ]
                )
            )

        final_months.append(
            month
        )

    processed = processed[
        processed["GL"]
        != ""
    ]

    processed = (
        processed.groupby(
            "GL",
            as_index=False
        )
        .sum(
            numeric_only=True
        )
    )

    return (
        processed,
        final_months
    )
