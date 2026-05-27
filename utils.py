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

        row = df.iloc[i].astype(str)

        score = 0

        for cell in row:

            cell = str(cell).lower()

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

    # Remove fully blank rows
    df = df.dropna(how="all")

    # Remove fully blank columns
    df = df.dropna(axis=1, how="all")

    # Fill blanks
    df = df.fillna("")

    return df


def normalize_columns(df):

    cleaned_cols = []

    for col in df.columns:

        col = str(col)

        col = col.strip().lower()

        col = col.replace("\n", " ")

        col = re.sub(r"\s+", " ", col)

        cleaned_cols.append(col)

    df.columns = cleaned_cols

    return df


def detect_ledger_column(df):

    # First priority → keyword match
    for col in df.columns:

        col_clean = str(col).lower()

        if any(keyword in col_clean for keyword in LEDGER_KEYWORDS):
            return col

    # Second priority → text-heavy column
    text_ratio = {}

    for col in df.columns:

        try:

            sample = df[col].astype(str).head(30)

            text_count = sample.apply(
                lambda x: any(c.isalpha() for c in str(x))
            ).sum()

            text_ratio[col] = text_count

        except:
            continue

    if not text_ratio:
        raise Exception("Ledger column could not be detected.")

    return max(text_ratio, key=text_ratio.get)


def detect_amount_column(df):

    # First priority → keyword match
    for col in df.columns:

        col_clean = str(col).lower()

        if any(keyword in col_clean for keyword in AMOUNT_KEYWORDS):
            return col

    # Second priority → most numeric column
    numeric_scores = {}

    for col in df.columns:

        try:

            converted = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("(", "-", regex=False)
                .str.replace(")", "", regex=False),
                errors="coerce",
            )

            numeric_scores[col] = converted.notna().sum()

        except:
            continue

    if not numeric_scores:
        raise Exception("Amount column could not be detected.")

    return max(numeric_scores, key=numeric_scores.get)


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

    # Numeric-only rows
    if re.fullmatch(r"[\d\.\,\-]+", gl):
        return True

    # Very short junk rows
    if len(gl) <= 2:
        return True

    return False


def preprocess_mis(df):

    # Initial cleaning
    df = clean_dataframe(df)

    if df.empty:
        raise Exception("Uploaded file is empty.")

    # Detect header row
    header_row = detect_header_row(df)

    # Assign headers safely
    df.columns = [
        str(col).strip()
        for col in df.iloc[header_row].values
    ]

    # Remove header rows
    df = df[(header_row + 1):]

    # Reset index
    df = df.reset_index(drop=True)

    # Normalize columns
    df = normalize_columns(df)

    if df.empty:
        raise Exception("No usable data found after preprocessing.")

    # Detect columns
    ledger_col = detect_ledger_column(df)

    amount_col = detect_amount_column(df)

    # Create processed dataframe
    processed = pd.DataFrame()

    processed["GL"] = (
        df[ledger_col]
        .astype(str)
        .str.strip()
    )

    processed["Amount"] = clean_amount_column(
        df[amount_col]
    )

    # Remove invalid rows
    processed = processed[
        ~processed["GL"].apply(is_invalid_row)
    ]

    if processed.empty:
        raise Exception("No valid ledger rows found.")

    # Group duplicate GLs
    processed = (
        processed.groupby("GL", as_index=False)["Amount"]
        .sum()
    )

    return processed
