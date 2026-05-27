import pandas as pd
import numpy as np
import re


LEDGER_KEYWORDS = [
    "gl",
    "ledger",
    "particular",
    "particulars",
    "account",
    "account name",
    "ledger name",
    "g/l",
]

MONTH_KEYWORDS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
    "202",
]


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

        elif filename.endswith(".txt"):
            df = pd.read_csv(
                uploaded_file,
                sep=None,
                engine="python",
                header=None
            )

        elif filename.endswith(".ods"):
            df = pd.read_excel(
                uploaded_file,
                header=None,
                engine="odf"
            )

        else:
            raise ValueError("Unsupported file format.")

        return df

    except Exception as e:
        raise Exception(f"Error reading file: {e}")


def clean_dataframe(df):

    df = df.copy()

    df = df.dropna(how="all")

    df = df.dropna(axis=1, how="all")

    df = df.fillna("")

    return df


def detect_header_row(df, max_scan_rows=15):

    best_row = 0
    best_score = 0

    for i in range(min(max_scan_rows, len(df))):

        row = df.iloc[i].astype(str)

        score = 0

        for cell in row:

            cell = str(cell).lower()

            if any(k in cell for k in LEDGER_KEYWORDS):
                score += 5

            if any(k in cell for k in MONTH_KEYWORDS):
                score += 2

        if score > best_score:

            best_score = score
            best_row = i

    return best_row


def normalize_columns(df):

    cleaned_cols = []

    seen = {}

    for col in df.columns:

        col = str(col)

        col = col.strip().lower()

        col = col.replace("\n", " ")

        col = re.sub(r"\s+", " ", col)

        # Handle duplicate column names
        if col in seen:

            seen[col] += 1

            col = f"{col}_{seen[col]}"

        else:

            seen[col] = 0

        cleaned_cols.append(col)

    df.columns = cleaned_cols

    return df


def detect_ledger_column(df):

    for col in df.columns:

        col_clean = str(col).lower()

        if any(k in col_clean for k in LEDGER_KEYWORDS):
            return col

    raise Exception("Ledger column not detected.")


def detect_month_columns(df):

    month_cols = []

    for col in df.columns:

        col_str = str(col).lower()

        if (
            any(m in col_str for m in MONTH_KEYWORDS)
            or "-" in col_str
            or "/" in col_str
        ):

            month_cols.append(col)

    if not month_cols:
        raise Exception("Month columns not detected.")

    return month_cols


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

    if gl == "":
        return True

    invalid_keywords = [
        "total",
        "subtotal",
        "grand total",
        "entry to be passed",
        "narration",
    ]

    if any(word in gl for word in invalid_keywords):
        return True

    if re.fullmatch(r"[\d\.\,\-]+", gl):
        return True

    if len(gl) <= 2:
        return True

    return False


def preprocess_mis(df):

    df = clean_dataframe(df)

    if df.empty:
        raise Exception("Uploaded file is empty.")

    header_row = detect_header_row(df)

    df.columns = [
        str(col).strip()
        for col in df.iloc[header_row].values
    ]

    df = df[(header_row + 1):]

    df = df.reset_index(drop=True)

    df = normalize_columns(df)

    ledger_col = detect_ledger_column(df)

    month_cols = detect_month_columns(df)

    processed = pd.DataFrame()

    processed["GL"] = (
        df[ledger_col]
        .astype(str)
        .str.strip()
    )

    processed = processed[
        ~processed["GL"].apply(is_invalid_row)
    ]

    for month in month_cols:

    col_data = df[month]

    # If duplicate columns return DataFrame
    if isinstance(col_data, pd.DataFrame):

        col_data = col_data.iloc[:, 0]

    processed[month] = clean_amount_column(
        col_data
    )

    processed = (
        processed.groupby("GL", as_index=False)
        .sum(numeric_only=True)
    )

    return processed, month_cols
