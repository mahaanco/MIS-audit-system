import pandas as pd
import numpy as np
import re
from io import BytesIO


LEDGER_KEYWORDS = [
    "gl",
    "ledger",
    "particular",
    "particulars",
    "account",
    "account name",
    "ledger name",
    "g/l",
    "g/l account",
]

AMOUNT_KEYWORDS = [
    "amount",
    "amt",
    "balance",
    "value",
    "closing",
    "current",
    "debit",
    "credit",
    "net",
]


def read_file(uploaded_file):

    filename = uploaded_file.name.lower()

    try:

        if filename.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        elif filename.endswith(".xls"):
            df = pd.read_excel(uploaded_file, engine="xlrd")

        elif filename.endswith(".xlsb"):
            df = pd.read_excel(uploaded_file, engine="pyxlsb")

        elif filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif filename.endswith(".txt"):
            df = pd.read_csv(uploaded_file, sep=None, engine="python")

        elif filename.endswith(".ods"):
            df = pd.read_excel(uploaded_file, engine="odf")

        else:
            raise ValueError("Unsupported file format.")

        return df

    except Exception as e:
        raise Exception(f"Error reading file {uploaded_file.name}: {e}")


def detect_header_row(df, max_scan_rows=15):

    best_row = 0
    best_score = 0

    for i in range(min(max_scan_rows, len(df))):

        row = df.iloc[i].astype(str).str.lower()

        score = 0

        for cell in row:
            if any(keyword in cell for keyword in LEDGER_KEYWORDS):
                score += 2

            if any(keyword in cell for keyword in AMOUNT_KEYWORDS):
                score += 2

        if score > best_score:
            best_score = score
            best_row = i

    return best_row


def clean_dataframe(df):

    df = df.copy()

    df = df.dropna(how="all")

    df = df.fillna("")

    return df


def normalize_columns(df):

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\n", " ", regex=True)
    )

    return df


def detect_ledger_column(df):

    for col in df.columns:

        col_clean = str(col).lower()

        if any(keyword in col_clean for keyword in LEDGER_KEYWORDS):
            return col

    text_ratio = {}

    for col in df.columns:

        sample = df[col].astype(str).head(30)

        text_count = sample.apply(lambda x: any(c.isalpha() for c in x)).sum()

        text_ratio[col] = text_count

    return max(text_ratio, key=text_ratio.get)


def detect_amount_column(df):

    for col in df.columns:

        col_clean = str(col).lower()

        if any(keyword in col_clean for keyword in AMOUNT_KEYWORDS):
            return col

    numeric_scores = {}

    for col in df.columns:

        converted = pd.to_numeric(
            df[col].astype(str).str.replace(",", ""),
            errors="coerce",
        )

        numeric_scores[col] = converted.notna().sum()

    return max(numeric_scores, key=numeric_scores.get)


def clean_amount_column(series):

    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "")
        .str.replace("(", "-")
        .str.replace(")", "")
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

    if gl.isnumeric():
        return True

    if len(gl) <= 2:
        return True

    return False


def preprocess_mis(df):

    df = clean_dataframe(df)

    header_row = detect_header_row(df)

    df.columns = df.iloc[header_row]

    df = df[(header_row + 1):]

    df = normalize_columns(df)

    ledger_col = detect_ledger_column(df)

    amount_col = detect_amount_column(df)

    processed = pd.DataFrame()

    processed["GL"] = df[ledger_col].astype(str).str.strip()

    processed["Amount"] = clean_amount_column(df[amount_col])

    processed = processed[~processed["GL"].apply(is_invalid_row)]

    processed = processed.groupby("GL", as_index=False)["Amount"].sum()

    return processed
