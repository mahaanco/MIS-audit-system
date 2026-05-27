
    col_str = str(col).lower()

    # Ignore timestamp/time columns
    if ":" in col_str:
        continue

    # Detect only month/date columns
    if (
        "-" in col_str
        or "/" in col_str
        or "202" in col_str
    ):

        # Remove time portion if exists
        clean_col = (
            str(col)
            .split(" ")[0]
            .strip()
        )

        month_cols.append(clean_col)

            month_cols.append(col)

    # Create processed dataframe
    processed = pd.DataFrame()

    processed["GL"] = (
        df[ledger_col]
        .astype(str)
        .str.strip()
    )

    # Remove invalid rows
    processed = processed[
        ~processed["GL"].apply(is_invalid_row)
    ]

    # Add month columns
    for month in month_cols:

        col_data = df[month]

        if isinstance(col_data, pd.DataFrame):

            col_data = col_data.iloc[:, 0]

        processed[month] = clean_amount_column(
            col_data
        )

    # Remove blanks
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
