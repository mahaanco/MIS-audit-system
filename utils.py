import pandas as pd
import re


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

    # Remove blank rows
    df = df.dropna(how="all")

    # Remove blank columns
    df = df.dropna(axis=1, how="all")

    # Fill NA
    df = df.fillna("")

    return df


def normalize_columns(df):

    cleaned_cols = []

    seen = {}

    for col in df.columns:

        col = str(col)

        col = col.strip().lower()

        col = col.replace("\n", " ")

        col = re.sub(r"\s+", " ", col)

        # Handle duplicate columns
        if col in seen:

            seen[col] += 1

            col = f"{col}_{seen[col]}"

        else:

            seen[col] = 0

        cleaned_cols.append(col)

    df.columns = cleaned_cols

    return df


def clean_amount_column(series):

    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("(", "-", regex=False)
        .str.replace(")", "", regex=False)
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

    # Numeric-only rows
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

        if str(col).lower() in possible_columns:

            return col

    raise Exception(
        "Ledger column not found."
    )


def detect_month_and_drcr_columns(df):

    month_data = {}

    for col in df.columns:

        col_str = str(col).lower()

        # Remove timestamp
        clean_col = (
            col_str
            .split(" ")[0]
            .strip()
        )

        # Detect DR columns
        if (
            "debit" in clean_col
            or clean_col.endswith("dr")
        ):

            month_name = (
                clean_col
                .replace("debit", "")
                .replace("dr", "")
                .strip()
            )

            if month_name not in month_data:

                month_data[month_name] = {}

            month_data[month_name]["debit"] = col

        # Detect CR columns
        elif (
            "credit" in clean_col
            or clean_col.endswith("cr")
        ):

            month_name = (
                clean_col
                .replace("credit", "")
                .replace("cr", "")
                .strip()
            )

            if month_name not in month_data:

                month_data[month_name] = {}

            month_data[month_name]["credit"] = col

        # Detect single amount columns
        elif (
            "-" in clean_col
            or "/" in clean_col
            or "202" in clean_col
        ):

            if clean_col not in month_data:

                month_data[clean_col] = {}

            month_data[clean_col]["amount"] = col

    return month_data


def preprocess_mis(df):

    # Clean dataframe
    df = clean_dataframe(df)

    # Fixed header row
    header_row = 3

    # Assign headers
    df.columns = [
        str(col).strip()
        for col in df.iloc[header_row]
    ]

    # Remove upper rows
    df = df[(header_row + 1):]

    # Reset index
    df = df.reset_index(drop=True)

    # Normalize columns
    df = normalize_columns(df)

    # Detect ledger column
    ledger_col = detect_ledger_column(df)

    # Detect month structures
    month_data = detect_month_and_drcr_columns(df)

    # Create processed dataframe
    processed = pd.DataFrame()

    processed["GL"] = (
        df[ledger_col]
        .astype(str)
        .str.strip()
    )

    # Remove invalid rows
    processed = processed[
        ~processed["GL"].apply(
            is_invalid_row
        )
    ]

    final_months = []

    # Process month columns
    for month, cols in month_data.items():

        # DR/CR format
        if (
            "debit" in cols
            or "credit" in cols
        ):

            debit_values = 0

            credit_values = 0

            if "debit" in cols:

                debit_col = cols["debit"]

                debit_values = (
                    clean_amount_column(
                        df[debit_col]
                    )
                )

            if "credit" in cols:

                credit_col = cols["credit"]

                credit_values = (
                    clean_amount_column(
                        df[credit_col]
                    )
                )

            processed[month] = (
                debit_values
                - credit_values
            )

            final_months.append(month)

        # Single amount format
        elif "amount" in cols:

            amount_col = cols["amount"]

            processed[month] = (
                clean_amount_column(
                    df[amount_col]
                )
            )

            final_months.append(month)

    # Remove blank GLs
    processed = processed[
        processed["GL"].notna()
    ]

    processed = processed[
        processed["GL"] != ""
    ]

    # Group duplicate GLs
    processed = (
        processed.groupby(
            "GL",
            as_index=False
        )
        .sum(numeric_only=True)
    )

    return processed, final_months
