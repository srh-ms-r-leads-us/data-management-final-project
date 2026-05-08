"""
TabPy script: Data quality scoring for RAW data (BEFORE cleaning).
Function name in Tableau Prep: compute_raw_quality_score

This script is designed to run on the RAW input data — meaning columns
still have string types, embedded units (cm, kg, €), star symbols, etc.

It produces the SAME output schema as the post-cleaning quality script
(Completeness_Score, Validity_Score, Consistency_Score, Quality_Score,
Quality_Tier) so the before/after numbers are directly comparable.

VALIDITY checks here verify FORMAT cleanliness:
  - Is Height a plain numeric value? (not "187cm" or "5'10\"")
  - Is Weight clean? (not "72kg" or "159lbs")
  - Are star ratings (W/F, SM, IR) plain integers? (not "4 ★")
  - Is Value a plain number? (not "€103.5M")
  - Is Hits a plain integer? (not "1.6K")
  - Does Club have no embedded newlines?

CONSISTENCY checks remain similar:
  - POT >= OVA
  - Contract format is parseable

Use this script BEFORE the cleaning steps in your flow, on the raw input.
"""

import pandas as pd
import numpy as np
import re


def compute_raw_quality_score(df):
    df = df.copy()

    # --- Completeness: % of critical fields populated ---
    critical_fields = [
        "ID", "Name", "Nationality", "Age", "Club",
        "Height", "Weight", "Value", "Wage", "Best Position"
    ]
    available = [c for c in critical_fields if c in df.columns]
    completeness = df[available].notna().sum(axis=1) / len(available) * 100

    # --- Validity: format cleanliness checks ---
    def check_height(v):
        if pd.isna(v):
            return 0
        # Clean format would be just a number (no "cm" or feet/inches)
        s = str(v).strip()
        return 1 if re.match(r'^\d+$', s) else 0

    def check_weight(v):
        if pd.isna(v):
            return 0
        s = str(v).strip()
        return 1 if re.match(r'^\d+$', s) else 0

    def check_currency(v):
        if pd.isna(v):
            return 0
        s = str(v).strip()
        # Clean = plain number; messy = has €, M, K, comma
        return 1 if re.match(r'^[\d.]+$', s) else 0

    def check_star_rating(v):
        if pd.isna(v):
            return 0
        s = str(v).strip()
        return 1 if re.match(r'^\d+$', s) else 0

    def check_hits(v):
        if pd.isna(v):
            return 0
        s = str(v).strip()
        return 1 if re.match(r'^\d+$', s) else 0

    def check_club(v):
        if pd.isna(v):
            return 0
        s = str(v)
        return 1 if ('\n' not in s and '\r' not in s) else 0

    valid = pd.Series(0, index=df.index)
    checks = 0
    if "Height" in df.columns:
        valid += df["Height"].apply(check_height); checks += 1
    if "Weight" in df.columns:
        valid += df["Weight"].apply(check_weight); checks += 1
    if "Value" in df.columns:
        valid += df["Value"].apply(check_currency); checks += 1
    if "Wage" in df.columns:
        valid += df["Wage"].apply(check_currency); checks += 1
    if "W/F" in df.columns:
        valid += df["W/F"].apply(check_star_rating); checks += 1
    if "SM" in df.columns:
        valid += df["SM"].apply(check_star_rating); checks += 1
    if "IR" in df.columns:
        valid += df["IR"].apply(check_star_rating); checks += 1
    if "Hits" in df.columns:
        valid += df["Hits"].apply(check_hits); checks += 1
    if "Club" in df.columns:
        valid += df["Club"].apply(check_club); checks += 1

    validity = (valid / checks * 100) if checks else pd.Series(100.0, index=df.index)

    # --- Consistency: logical constraints ---
    cons = pd.Series(0, index=df.index)
    cons_checks = 0
    if {"OVA", "POT"}.issubset(df.columns):
        cons += (df["POT"] >= df["OVA"]).fillna(False).astype(int); cons_checks += 1
    # Contract format check: should be "YYYY ~ YYYY" or "Free" or contain "On Loan"
    if "Contract" in df.columns:
        def check_contract(v):
            if pd.isna(v):
                return 0
            s = str(v)
            if s == "Free":
                return 1
            if "On Loan" in s:
                return 1
            if re.match(r'^\d{4} ~ \d{4}$', s):
                return 1
            return 0
        cons += df["Contract"].apply(check_contract); cons_checks += 1
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
    """Schema for raw input columns. We output ONLY the identification fields
    plus the new quality score columns — keeps the output small and focused
    on the comparison."""
    return pd.DataFrame({
        "ID": prep_int(),
        "Name": prep_string(),
        "Nationality": prep_string(),
        "Age": prep_int(),
        "OVA": prep_int(),
        "POT": prep_int(),
        # NEW from this script
        "Completeness_Score": prep_decimal(),
        "Validity_Score": prep_decimal(),
        "Consistency_Score": prep_decimal(),
        "Quality_Score": prep_decimal(),
        "Quality_Tier": prep_string(),
    })
