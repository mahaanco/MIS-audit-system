import pandas as pd
import re


def read_file(uploaded_file):

    filename = uploaded_file.name.lower()

    if filename.endswith(".xlsx"):

        return pd.read_excel(
            uploaded_file,
            header=None,
            engine="openpyxl"
        )

    elif filename.endswith(".xls"):

        return pd.read_excel(
            uploaded_file,
            header=None,
            engine="xlrd"
        )

    elif filename.endswith(".xlsb"):

        return pd.read_excel(
            uploaded_file,
            header=None,
            engine="pyxlsb"
        )

    elif filename.endswith(".csv"):

        return pd.read_csv(
            uploaded_file,
            header=None
        )

    else:

        raise Exception(
            "Unsupported file format."
        )


def clean_dataframe(df):

    df = df.copy()

    df = df.dropna(how="all")

    df = df.dropna(axis=1, how="all")

    df = df.fillna("")

    return df


def normalize_columns(df):

    cleaned_cols = []

    seen = {}

    for col in df.columns:

        col = str(col)

        col = col.strip().lower()

        col = re.sub(r"\s+", " ", col)

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

    if re.fullmatch(
        r"[\d\.\,\-]+",
        gl
    ):
        return True

    return False


def preprocess_mis(df):

    # Clean dataframe
    df = clean_dataframe(df)

    # Header row in your MIS
    header_row = 3

    # Set headers
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

    # Ledger column
    ledger_col = "gl name"

    # Detect month columns
    month_cols = []

    month_mapping = {}

    for col in df.columns:

        col_str = str(col).lower()

        if (
            "-" in col_str
            or "/" in col_str
            or "202" in col_str
        ):

            clean_col = (
                str(col)
                .split(" ")[0]
                .strip()
            )

            month_cols.append(clean_col)

            month_mapping[
                clean_col
            ] = col

    # Remove duplicates
    month_cols = list(
        dict.fromkeys(month_cols)
    )

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

    # Add month columns
    for month in month_cols:

        original_col = month_mapping[
            month
        ]

        col_data = df[original_col]

        if isinstance(
            col_data,
            pd.DataFrame
        ):

            col_data = col_data.iloc[:, 0]

        processed[month] = (
            clean_amount_column(
                col_data
            )
        )

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

    return processed, month_cols
