"""
TabPy script: Row-level data quality scoring.
Function name in Tableau Prep: compute_quality_score

Insert AFTER the KMeans Archetype Clustering step.

Adds five new columns:
  - Completeness_Score (0-100)
  - Validity_Score (0-100)
  - Consistency_Score (0-100)
  - Quality_Score (weighted overall, 0-100)
  - Quality_Tier (Poor/Fair/Good/Excellent)
"""

import pandas as pd
import numpy as np


def compute_quality_score(df):
    df = df.copy()

    critical_fields = [
        "ID", "Name", "Nationality", "Age", "OVA", "Club",
        "Height", "Weight", "Value", "Wage", "Best Position"
    ]
    available = [c for c in critical_fields if c in df.columns]
    completeness = df[available].notna().sum(axis=1) / len(available) * 100

    valid = pd.Series(0, index=df.index)
    checks = 0
    if "Age" in df.columns:
        valid += df["Age"].between(15, 50).fillna(False).astype(int); checks += 1
    if "OVA" in df.columns:
        valid += df["OVA"].between(40, 99).fillna(False).astype(int); checks += 1
    if "Height" in df.columns:
        valid += df["Height"].between(150, 220).fillna(False).astype(int); checks += 1
    if "Weight" in df.columns:
        valid += df["Weight"].between(45, 120).fillna(False).astype(int); checks += 1
    if "Value" in df.columns:
        valid += (df["Value"] >= 0).fillna(False).astype(int); checks += 1
    validity = (valid / checks * 100) if checks else pd.Series(100.0, index=df.index)

    cons = pd.Series(0, index=df.index)
    cons_checks = 0
    if {"OVA", "POT"}.issubset(df.columns):
        cons += (df["POT"] >= df["OVA"]).fillna(False).astype(int); cons_checks += 1
    if {"Contract_Start", "Contract_End"}.issubset(df.columns):
        ok = (df["Contract_End"] >= df["Contract_Start"]) | df["Contract_Start"].isna()
        cons += ok.fillna(True).astype(int); cons_checks += 1
    consistency = (cons / cons_checks * 100) if cons_checks else pd.Series(100.0, index=df.index)

    df["Completeness_Score"] = completeness.round(1).astype(float)
    df["Validity_Score"] = validity.round(1).astype(float)
    df["Consistency_Score"] = consistency.round(1).astype(float)
    df["Quality_Score"] = (
        completeness * 0.4 + validity * 0.4 + consistency * 0.2
    ).round(1).astype(float)

    df["Quality_Tier"] = pd.cut(
        df["Quality_Score"],
        bins=[0, 60, 75, 90, 101],
        labels=["Poor", "Fair", "Good", "Excellent"],
        right=False
    ).astype(str)

    return df


def get_output_schema():
    return pd.DataFrame({
        "ID": prep_int(),
        "Name": prep_string(),
        "LongName": prep_string(),
        "Nationality": prep_string(),
        "Confederation": prep_string(),
        "Continent": prep_string(),
        "Age": prep_int(),
        "OVA": prep_int(),
        "POT": prep_int(),
        "BOV": prep_int(),
        "Best Position": prep_string(),
        "Positions": prep_string(),
        "Preferred Foot": prep_string(),
        "Value": prep_decimal(),
        "Wage": prep_decimal(),
        "Release Clause": prep_decimal(),
        "Height": prep_int(),
        "Weight": prep_int(),
        "WF": prep_int(),
        "SM": prep_int(),
        "IR": prep_int(),
        #"Hits": prep_int(),
        "PAC": prep_int(),
        "SHO": prep_int(),
        "PAS": prep_int(),
        "DRI": prep_int(),
        "DEF": prep_int(),
        "PHY": prep_int(),
        "Total Stats": prep_int(),
        "Base Stats": prep_int(),
        "A/W": prep_string(),
        "D/W": prep_string(),
        "Contract_Status": prep_string(),
        "Contract_Start": prep_int(),
        "Contract_End": prep_int(),
        "Club": prep_string(),
        "Joined": prep_date(),
        "Loan Date End": prep_date(),
        "Age_Group": prep_string(),
        "Contract_Urgency": prep_string(),
        "Wage_Value_Flag": prep_string(),
        "Is_On_Loan": prep_string(),
        # From KMeans step (upstream)
        "Archetype": prep_int(),
        "Archetype_Label": prep_string(),
        # NEW from this script
        "Completeness_Score": prep_decimal(),
        "Validity_Score": prep_decimal(),
        "Consistency_Score": prep_decimal(),
        "Quality_Score": prep_decimal(),
        "Quality_Tier": prep_string(),
    })
