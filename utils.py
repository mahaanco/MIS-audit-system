import pandas as pd
import streamlit as st
import zipfile
import json
import xml.etree.ElementTree as ET

from io import BytesIO

def detect_header_row(df):

    for i in range(min(20, len(df))):

        row = (
            df.iloc[i]
            .astype(str)
            .str.lower()
        )

        keywords = [

            "gl name",
            "particular",
            "particulars",
            "ledger",
            "mapping",
            "description"
        ]

        if any(
            keyword in row.values
            for keyword in keywords
        ):
            return i

    return 0


def clean_columns(df):

    df.columns = (

        df.columns
        .astype(str)
        .str.strip()
    )

    return df


def read_excel_dynamic(file):

    raw_df = pd.read_excel(
        file,
        header=None
    )

    header_row = detect_header_row(raw_df)

    df = pd.read_excel(
        file,
        header=header_row
    )

    return clean_columns(df)


def read_csv_dynamic(file):

    raw_df = pd.read_csv(
        file,
        header=None
    )

    header_row = detect_header_row(raw_df)

    df = pd.read_csv(
        file,
        header=header_row
    )

    return clean_columns(df)


def read_txt_dynamic(file):

    df = pd.read_csv(
        file,
        sep=None,
        engine="python"
    )

    return clean_columns(df)


def read_json_dynamic(file):

    data = json.load(file)

    df = pd.json_normalize(data)

    return clean_columns(df)


def read_xml_dynamic(file):

    tree = ET.parse(file)

    root = tree.getroot()

    data = []

    for child in root:

        row = {}

        for item in child:
            row[item.tag] = item.text

        data.append(row)

    df = pd.DataFrame(data)

    return clean_columns(df)


def read_html_dynamic(file):

    dfs = pd.read_html(file)

    return clean_columns(dfs[0])


def read_parquet_dynamic(file):

    df = pd.read_parquet(file)

    return clean_columns(df)


def read_xlsb_dynamic(file):

    df = pd.read_excel(
        file,
        engine="pyxlsb"
    )

    return clean_columns(df)


def read_ods_dynamic(file):

    df = pd.read_excel(
        file,
        engine="odf"
    )

    return clean_columns(df)


def read_zip_dynamic(file):

    with zipfile.ZipFile(file) as z:

        first_file = z.namelist()[0]

        with z.open(first_file) as f:

            if first_file.endswith(".csv"):

                df = pd.read_csv(f)

            else:

                df = pd.read_excel(f)

    return clean_columns(df)


def read_mis_file(uploaded_file):

    file_name = (
        uploaded_file.name
        .lower()
    )

    try:

        if file_name.endswith(".xlsx"):
            return read_excel_dynamic(uploaded_file)

        elif file_name.endswith(".xls"):
            return read_excel_dynamic(uploaded_file)

        elif file_name.endswith(".xlsb"):
            return read_xlsb_dynamic(uploaded_file)

        elif file_name.endswith(".csv"):
            return read_csv_dynamic(uploaded_file)

        elif file_name.endswith(".txt"):
            return read_txt_dynamic(uploaded_file)

        elif file_name.endswith(".json"):
            return read_json_dynamic(uploaded_file)

        elif file_name.endswith(".xml"):
            return read_xml_dynamic(uploaded_file)

        elif file_name.endswith(".html"):
            return read_html_dynamic(uploaded_file)

        elif file_name.endswith(".parquet"):
            return read_parquet_dynamic(uploaded_file)

        elif file_name.endswith(".ods"):
            return read_ods_dynamic(uploaded_file)

        elif file_name.endswith(".zip"):
            return read_zip_dynamic(uploaded_file)

        else:

            st.error(
                f"Unsupported File Type: {file_name}"
            )

            return pd.DataFrame()

    except Exception as e:

        st.error(
            f"Error Reading File: {e}"
        )

        return pd.DataFrame()
