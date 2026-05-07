import pandas as pd


def process_contract(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Create new columns
    df["ContractStart"] = None
    df["ContractEnd"] = None
    df["LoanDateEnd"] = None
    df["ContractType"] = None

    # Permanent contracts: "2018 ~ 2024"
    permanent_mask = df["Contract"].str.contains("~", na=False)

    df.loc[permanent_mask, "ContractStart"] = (
        df.loc[permanent_mask, "Contract"]
        .str.split("~")
        .str[0]
        .str.strip()
        .astype("Int64")
    )

    df.loc[permanent_mask, "ContractEnd"] = (
        df.loc[permanent_mask, "Contract"]
        .str.split("~")
        .str[1]
        .str.strip()
        .astype("Int64")
    )

    df.loc[permanent_mask, "ContractType"] = "permanent"

    # Loan contracts: "Jun 30, 2021 On Loan"
    loan_mask = df["Contract"].str.contains("On Loan", na=False)

    loan_dates = pd.to_datetime(
        df.loc[loan_mask, "Contract"].str.replace(" On Loan", "", regex=False),
        format="%b %d, %Y",
        errors="coerce"
    )

    df.loc[loan_mask, "LoanDateEnd"] = (
        loan_dates.dt.strftime("%Y-%m-%d").where(loan_dates.notna(), None)
    )

    df.loc[loan_mask, "ContractType"] = "loan"

    # Free agents
    free_mask = df["Contract"].eq("Free")

    df.loc[free_mask, "ContractType"] = "free_agent"

    return df


def process_positions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Split positions into separate columns
    positions_split = df["Positions"].str.split(",", expand=True)

    # Create position columns
    df["Position1"] = positions_split[0].str.strip()

    df["Position2"] = (
        positions_split[1].str.strip()
        if positions_split.shape[1] > 1
        else None
    )

    df["Position3"] = (
        positions_split[2].str.strip()
        if positions_split.shape[1] > 2
        else None
    )

    return df


def process(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = process_contract(df)
    df = process_positions(df)

    return df


def get_output_schema():
    return pd.DataFrame({
        "ID": prep_int(),
        "ContractStart": prep_int(),
        "ContractEnd": prep_int(),
        "LoanDateEnd": prep_string(),
        "ContractType": prep_string(),
        "Position1": prep_string(),
        "Position2": prep_string(),
        "Position3": prep_string(),
    })


if __name__ == '__main__':
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)

    test_df = pd.DataFrame({
        "Contract": [
            "2018 ~ 2024",
            "Jun 30, 2021 On Loan",
            "Free"
        ],
        "Positions": [
            "RW, ST, CF",
            "CAM, CM",
            "GK"
        ]
    })

    test_df = process(test_df)
    print(test_df)
