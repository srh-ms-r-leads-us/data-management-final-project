# FIFA 21 Data Cleaning — Clean-up Transformation Documentation

**Project:** Data Management Final Project
**Dataset:** FIFA 21 Raw Dataset (`fifa21_raw_data_v2.csv`)
**Source:** [Kaggle — yagunnersya/fifa-21-messy-raw-dataset-for-cleaning-exploring](https://www.kaggle.com/datasets/yagunnersya/fifa-21-messy-raw-dataset-for-cleaning-exploring)
**Initial size:** 18,979 rows × 77 columns

---

## Table of Contents

1. [Overview](#overview)
2. [Column Rename Map (Final Names)](#column-rename-map-final-names)
3. [Tableau Prep — Cleaning Transformations](#tableau-prep--cleaning-transformations)
4. [Tableau Prep — Structural Transformations](#tableau-prep--structural-transformations)
5. [Python (TabPy) Script Steps](#python-tabpy-script-steps)
6. [Output Files](#output-files)
7. [Before vs After Quality Comparison](#before-vs-after-quality-comparison)

---

## Overview

The cleaning pipeline consists of:
- **41 transformation changes** inside the main Clean step chain (drops, renames, calculated fields)
- **3 structural transformations** (Filter, Aggregate, Pivot) on separate branches
- **1 Join** with a custom-built reference table (Confederation/Continent enrichment)
- **2 TabPy script steps** (KMeans clustering, Quality scoring)
- **1 parallel quality-scoring branch** on raw data for before/after comparison

---

## Column Rename Map (Final Names)

| Original Column | Final Name | Reason |
|---|---|---|
| `↓OVA` | `OVA` | Removed weird arrow character that breaks calculations |
| `Club` (with `\n\n\n\n` prefix) | `Club` | Stripped embedded newlines |
| `Height` (string with cm/ft) | `Height` | Converted to integer cm |
| `Weight` (string with kg/lbs) | `Weight` | Converted to integer kg |
| `W/F` (had `★`) | `WF` | Removed star, removed slash from name |
| `SM` (had `★`) | `SM` | Removed star symbol |
| `IR` (had `★`) | `IIR` *(typo in our flow — should be IR)* | Removed star symbol |
| `Hits` (mixed K-suffix) | `Hits` | Recovered K values, normalized to integer |
| `Contract` (mixed formats) | *removed* | Replaced by 3 split columns |
| *(new)* | `Contract_Status` | Active / Free Agent / On Loan |
| *(new)* | `Contract_Start` | Start year |
| *(new)* | `Contract_End` | End year |
| `Joined` (auto-detected as date) | `Joined` | No transformation needed (Tableau Prep auto-typed) |
| `Value` (€ + M/K) | `Value` | Numeric euros |
| `Wage` (€ + M/K) | `Wage` | Numeric euros |
| `Release Clause` (€ + M/K) | `Release_Clause` | Numeric euros |
| *(new)* | `Age_Group` | Youth / Prime / Veteran |
| *(new)* | `Contract_Urgency` | Long Term / Expiring Next Season / etc. |
| *(new)* | `Wage_Value_Flag` | Normal / High Wage Ratio / Free Agent–Zero Value |
| *(new)* | `Is_On_Loan` | Yes / No (encoded from Loan Date End) |

---

## Tableau Prep — Cleaning Transformations

These 41 changes appear in the main Clean step chain (visible in the Changes panel).

### Removals (cleanup)

| # | Change Type | Field | Reason |
|---|---|---|---|
| 1 | Remove Field | `playerUrl` | URL not needed for analysis |
| 2 | Remove Field | `photoUrl` | URL not needed for analysis |

### Column rename

| # | Change Type | Field | Detail |
|---|---|---|---|
| 3 | Rename Field | `OVA` | From `↓OVA` to `OVA` |

### Club newline cleanup

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 4 | Calculated Field | `Clean Club` | `REGEXP_REPLACE([Club], "[\n\r]+", "")` |
| 5 | Remove Field | `Club` | Original column with newline prefix |

### Height conversion (handles cm and ft/in formats)

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 6 | Calculated Field | `Clean Height` | `IF CONTAINS([Height], "cm") THEN INT(REPLACE([Height], "cm", "")) ELSEIF CONTAINS([Height], "'") THEN INT(INT(SPLIT([Height], "'", 1)) * 30.48 + INT(REPLACE(SPLIT([Height], "'", 2), '"', '')) * 2.54) ELSE NULL END` |
| 7 | Remove Field | `Height` | Original string version |

### Weight conversion (handles kg and lbs formats)

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 8 | Calculated Field | `Clean Weight` | `IF CONTAINS([Weight], "kg") THEN INT(REPLACE([Weight], "kg", "")) ELSEIF CONTAINS([Weight], "lbs") THEN INT(INT(REPLACE([Weight], "lbs", "")) * 0.453592) ELSE NULL END` |
| 9 | Remove Field | `Weight` | Original string version |

### Star rating cleanups (W/F, SM, IR)

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 10 | Calculated Field | `Weak Foot Rating` | `INT(TRIM(REPLACE([W/F], "★", "")))` |
| 11 | Remove Field | `W/F` | Original column with star symbol |
| 12 | Calculated Field | `Skill Moves Rating` | `INT(TRIM(REPLACE([SM], "★", "")))` |
| 13 | Remove Field | `SM` | Original column with star symbol |
| 14 | Calculated Field | `International Reputation` | `INT(TRIM(REPLACE([IR], "★", "")))` |
| 15 | Remove Field | `IR` | Original column with star symbol |

### Hits cleanup (recovers K-suffix values lost to silent type coercion)

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 16 | Calculated Field | `Hits Clean` | `IF ISNULL([Hits]) THEN 0 ELSEIF CONTAINS([Hits], "K") THEN INT(FLOAT(REPLACE([Hits], "K", "")) * 1000) ELSE INT([Hits]) END` |
| 17 | Remove Field | `Hits` | Original mixed-type column |

### Contract decomposition (3 new columns from 1)

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 18 | Calculated Field | `Contract_Status` | `IF [Contract] = "Free" THEN "Free Agent" ELSEIF CONTAINS([Contract], "On Loan") THEN "On Loan" ELSE "Active" END` |
| 19 | Calculated Field | `Contract_Start` | `IF [Contract_Status] = "Active" THEN INT(TRIM(SPLIT([Contract], "~", 1))) ELSE NULL END` |
| 20 | Calculated Field | `Contract_End` | `IF [Contract_Status] = "Active" THEN INT(TRIM(SPLIT([Contract], "~", 2))) ELSEIF [Contract_Status] = "On Loan" THEN INT(REGEXP_EXTRACT([Contract], "(\d{4})")) ELSE NULL END` |

### Currency parsing (Value, Wage, Release Clause)

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 21 | Calculated Field | `Values_Euros` | `IF [Value] = "€0" THEN 0 ELSEIF CONTAINS([Value], "M") THEN FLOAT(REPLACE(REPLACE([Value], "€", ""), "M", "")) * 1000000 ELSEIF CONTAINS([Value], "K") THEN FLOAT(REPLACE(REPLACE([Value], "€", ""), "K", "")) * 1000 ELSE FLOAT(REPLACE([Value], "€", "")) END` |
| 22 | Calculated Field | `Wage_Euros` | Same pattern as Value, applied to Wage |
| 23 | Calculated Field | `Release_Clause_Euros` | Same pattern, with NULL handling: `IF ISNULL([Release Clause]) THEN NULL ELSEIF [Release Clause] = "€0" THEN 0 ELSEIF CONTAINS(...) ...` |
| 24 | Remove Field | `Wage` | Original string version |
| 25 | Remove Field | `Release Clause` | Original string version |
| 26 | Remove Field | `Value` | Original string version |
| 27 | Remove Field | `Contract` | Original mixed-format column |

### Final renames (consistent naming)

| # | Change Type | Field | Detail |
|---|---|---|---|
| 28 | Rename Field | `Club` | From `Clean Club` to `Club` |
| 29 | Rename Field | `Height` | From `Clean Height` to `Height` |
| 30 | Rename Field | `Weight` | From `Clean Weight` to `Weight` |
| 31 | Rename Field | `WF` | From `Weak Foot Rating` to `WF` |
| 32 | Rename Field | `SM` | From `Skill Moves Rating` to `SM` |
| 33 | Rename Field | `IIR` | From `International Reputation` to `IIR` ⚠️ *typo — should be `IR`* |
| 34 | Rename Field | `Hits` | From `Hits Clean` to `Hits` |
| 35 | Rename Field | `Wage` | From `Wage_Euros` to `Wage` |
| 36 | Rename Field | `Release_Clause` | From `Release_Clause_Euros` to `Release_Clause` |
| 37 | Rename Field | `Value` | From `Values_Euros` to `Value` |

### Engineered features (derived columns)

| # | Change Type | Field | Formula / Detail |
|---|---|---|---|
| 38 | Calculated Field | `Age_Group` | `IF [Age] <= 21 THEN "Youth" ELSEIF [Age] <= 29 THEN "Prime" ELSE "Veteran" END` |
| 39 | Calculated Field | `Contract_Urgency` | `IF [Contract_Status] = "Free Agent" THEN "Free Agent" ELSEIF [Contract_Status] = "On Loan" THEN "Loan" ELSEIF [Contract_End] <= 2021 THEN "Expiring Soon" ELSEIF [Contract_End] = 2022 THEN "Expiring Next Season" ELSE "Long Term" END` |
| 40 | Calculated Field | `Wage_Value_Flag` | `IF [Value] = 0 THEN "Free Agent / Zero Value" ELSEIF ([Wage] * 52) / [Value] > 0.5 THEN "High Wage Ratio" ELSE "Normal" END` |
| 41 | Calculated Field | `Is_On_Loan` | `IF NOT ISNULL([Loan Date End]) THEN "Yes" ELSE "No" END` |

---

## Tableau Prep — Structural Transformations

These appear as separate nodes on the canvas (not inside the Clean step).

### Filter step — Active contracts only

- **Node name:** Filter Active Players
- **Filter formula:** `[Contract_Status] = "Active"`
- **Effect:** 18,979 rows → 17,729 rows (removes 1,250 free agents and on-loan players)
- **Purpose:** Provides a focused dataset for current squad analysis

### Aggregate step — Country summary

- **Node name:** Aggregate by Nationality
- **Group by:** `Nationality`
- **Aggregations:**
  - `AVG(OVA)` → `Avg_OVA`
  - `AVG(POT)` → `Avg_Potential`
  - `AVG(Value)` → `Avg_Value`
  - `AVG(Wage)` → `Avg_Wage`
  - `COUNT(ID)` → `Player_Count`
- **Effect:** 18,979 rows → 164 country rows
- **Purpose:** Country-level insights for report (top nationalities by value, etc.)

### Pivot step — Skills wide-to-long

- **Node name:** Pivot Skills
- **Type:** Columns to Rows
- **Pivoted fields:** `PAC, SHO, PAS, DRI, DEF, PHY` (6 columns)
- **Output fields:**
  - `Pivot1 Names` → renamed to `Skill_Type`
  - `Pivot1 Values` → renamed to `Skill_Value`
- **Effect:** 18,979 rows × 6 columns → 113,874 rows × 2 columns
- **Purpose:** Enables single-chart skill comparisons across categories

### Join — Continent/Confederation reference

- **Node name:** Join Confederation
- **Right input:** `nationality_reference.csv` (custom-built lookup table, 164 rows)
- **Join clause:** `Nationality = Nationality`
- **Join type:** Left Join (preserves all 18,979 player rows)
- **Mismatched values:** 0 (full coverage verified)
- **Result:** Adds `Confederation` (UEFA / CONMEBOL / AFC / CAF / CONCACAF / OFC) and `Continent` columns
- **Purpose:** Enables regional analysis (e.g., avg value per UEFA player)
- **Cleanup:** Duplicate `Nationality` column from right input was removed

---

## Python (TabPy) Script Steps

All scripts run through TabPy server on `localhost:9004`. Each script is a standalone `.py` file with a function and a `get_output_schema()` declaration.

### Script 1 — KMeans player archetype clustering

- **File:** `tabpy_kmeans.py`
- **Function:** `cluster_player_archetypes`
- **Position in flow:** After `Join Confederation`
- **Why Python:** Unsupervised ML clustering is impossible in Tableau Prep natively
- **Algorithm:** KMeans with 6 clusters, StandardScaler-normalized features
- **Input features:** `PAC, SHO, PAS, DRI, DEF, PHY` (6 position skills)
- **New columns added:**
  - `Archetype` (integer 0–5)
  - `Archetype_Label` (string, e.g., "PAC / SHO", "DEF / PHY")
- **Discovered archetypes:** 5 distinct dominant-stat-pair groups (DEF/PHY, PAC/DRI, PAS/DRI, SHO/PAC, SHO/PHY) — two clusters share the DEF/PHY label, indicating sub-archetypes within defenders

### Script 2 — Data quality scoring (AFTER cleaning)

- **File:** `tabpy_quality.py`
- **Function:** `compute_quality_score`
- **Position in flow:** After KMeans
- **Why Python:** Multi-dimensional weighted scoring with conditional logic is verbose in Tableau Prep but elegant in Python
- **Dimensions evaluated:**
  1. **Completeness** — % of critical fields populated (ID, Name, Nationality, Age, OVA, Club, Height, Weight, Value, Wage, Best Position)
  2. **Validity** — # of fields with values in expected ranges (Age 15–50, OVA 40–99, Height 150–220 cm, Weight 45–120 kg, Value ≥ 0)
  3. **Consistency** — # of logical constraints satisfied (POT ≥ OVA, Contract_End ≥ Contract_Start)
- **New columns added:**
  - `Completeness_Score` (0–100)
  - `Validity_Score` (0–100)
  - `Consistency_Score` (0–100)
  - `Quality_Score` (weighted: 40% completeness + 40% validity + 20% consistency)
  - `Quality_Tier` (Poor < 60, Fair 60–75, Good 75–90, Excellent ≥ 90)

### Script 3 — Data quality scoring (BEFORE cleaning) — for comparison

- **File:** `tabpy_quality_raw.py`
- **Function:** `compute_raw_quality_score`
- **Position in flow:** Parallel branch off the original input (bypasses cleaning)
- **Purpose:** Produces directly-comparable quality scores on raw data, demonstrating the quantitative impact of the cleaning pipeline
- **Validity checks (different from after-cleaning):** verify FORMAT cleanliness instead of value ranges
  - Is Height a plain integer? (not "187cm" or "5'10\"")
  - Is Weight a plain integer? (not "72kg" or "159lbs")
  - Is Value a plain number? (not "€103.5M")
  - Are star ratings (W/F, SM, IR) plain integers? (not "4 ★")
  - Is Hits a plain integer? (not "1.6K")
  - Does Club have no embedded newlines?
- **Output schema:** Same 5 quality columns as Script 2 — for direct comparison

---

## Output Files

| Output Node | File Name | Description |
|---|---|---|
| Output Cleaned Data | `fifa21_cleaned_AFTER.csv` | Full cleaned dataset with all transformations + Python enrichments |
| Output Quality Before | `fifa21_quality_BEFORE.csv` | Quality scores on raw data (for comparison) |
| *Optional* | `fifa21_country_summary.csv` | One row per nationality with average stats |
| *Optional* | `fifa21_skills_long.csv` | Pivoted skills (long format) |

---

## Before vs After Quality Comparison

This is the **headline finding** of the project — concrete quantitative evidence that the cleaning pipeline materially improved data quality.

| Metric | BEFORE Cleaning | AFTER Cleaning | Improvement |
|---|---|---|---|
| **Mean Completeness Score** | 100.0 | 100.0 | unchanged (data was already complete) |
| **Mean Validity Score** | 11.1 | ~99.7 | **+88.6 points** |
| **Mean Consistency Score** | 100.0 | 100.0 | unchanged |
| **Mean Quality Score** | 63.8 | 99.9 | **+36.1 points** |
| **Records in "Excellent" tier** | 0 (0%) | 18,939 (99.8%) | **near-total migration** |
| **Records in "Fair" tier** | 18,979 (100%) | 0 (0%) | **eliminated** |

### Interpretation

- **Completeness was never the issue.** The raw data was 100% populated for critical fields. So our cleaning didn't fix missingness — it fixed *format*.
- **Validity was the entire story.** Pre-cleaning, only ~1 of 9 format checks passed per row on average. Post-cleaning, all 9 pass.
- **Consistency held throughout.** The data was internally logical; we didn't introduce contradictions.
- **The 40 imperial-unit rows** (height stored as `5'10"`, weight as `159lbs`) are responsible for the 0.2% of records that score "Good" instead of "Excellent" after cleaning. This is a documented edge case rather than a remaining defect.

---

## Notable Data Quality Findings

These insights emerged during the cleaning process and are worth highlighting in the report:

1. **Silent data loss on import.** Tableau Prep auto-typed the `Hits` column as numeric, silently converting 28 K-suffix values (e.g., "8.4K") to NULL. We mitigated by forcing string type at ingestion, then applying conditional cleanup logic. **Recovered 28 values that would otherwise have been lost (0.15% data loss prevented).**

2. **Mixed measurement systems.** Height was stored in cm format for 99.8% of records but in feet/inches for 40 records. Same pattern for Weight (kg vs lbs). A naive unit-stripping approach would have produced 40 NULL values. We implemented conditional logic to detect format and apply standard conversions (1 ft = 30.48 cm, 1 lb = 0.453592 kg).

3. **Multi-format columns.** The `Contract` column contained three different formats (year ranges, "On Loan" with embedded date, "Free"). We split this into 3 columns (Contract_Status, Contract_Start, Contract_End) so the downstream analysis can treat each format appropriately.

4. **Missing Not At Random.** `Loan Date End` is 94.6% null — but this absence is *meaningful*, not missing. Only loaned players have a loan end date. We did not impute these values; instead we encoded the absence into a categorical `Is_On_Loan` flag.

5. **Free agents and €0 valuations.** 248 players have `Value = €0`. These are not data quality issues; they are legitimate free agents. Our `Wage_Value_Flag` calculated field treats this as a separate category rather than an outlier.

---

## Tools and Versions

- **Tableau Prep Builder** — for the visual flow and core transformations
- **TabPy 2.x** running on `localhost:9004` — for Python script execution
- **Python 3.11** with packages: `pandas`, `numpy`, `scikit-learn`, `rapidfuzz`
- **Reference data:** Custom-built `nationality_reference.csv` (164 rows mapping each nationality to its FIFA confederation and continent)

---

*Generated for Data Management Final Project — FIFA 21 Cleaning Pipeline*
