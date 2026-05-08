import pandas as pd


def process(df: pd.DataFrame) -> pd.DataFrame:
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


def get_output_schema():
    return pd.DataFrame({
        "ID": prep_int(),
        "Position1": prep_string(),
        "Position2": prep_string(),
        "Position3": prep_string(),
    })
