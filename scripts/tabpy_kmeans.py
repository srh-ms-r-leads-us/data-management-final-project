"""
TabPy script: KMeans player archetype clustering.
Function name in Tableau Prep: cluster_player_archetypes

Adds two new columns:
  - Archetype (int 0-5)
  - Archetype_Label (string, e.g., "PAC / SHO")
"""

import pandas as pd
import numpy as np


def cluster_player_archetypes(df):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    df = df.copy()
    feature_cols = ["PAC", "SHO", "PAS", "DRI", "DEF", "PHY"]
    X = df[feature_cols].fillna(df[feature_cols].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=6, random_state=42, n_init=10)
    df["Archetype"] = km.fit_predict(X_scaled).astype(int)

    centroids = km.cluster_centers_
    labels = []
    for c in centroids:
        top_idx = np.argsort(c)[::-1][:2]
        top_names = [feature_cols[i] for i in top_idx]
        labels.append(" / ".join(top_names))

    df["Archetype_Label"] = df["Archetype"].map(dict(enumerate(labels)))
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
        "Archetype": prep_int(),
        "Archetype_Label": prep_string(),
    })
