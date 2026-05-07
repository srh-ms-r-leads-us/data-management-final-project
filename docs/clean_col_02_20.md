# Cleaning Approach for the 2nd to 20th Columns

## ID

- A unique identifier column.

## Name

- No cleaning required.

## LongName

- No cleaning required.

## photoUrl

- Rename the column name to `PhotoUrl`

## playerUrl

- Rename the column name to `PlayerUrl`

## Nationality

- Standardize selected country names to more commonly recognized international forms for consistency and better geographic visualization.
  - `Korea Republic` → `South Korea`
  - `Korea DPR` → `North Korea`
  - `China PR` → `China`
  - `DR Congo` → `Democratic Republic of the Congo`
  - `Republic of Ireland` → `Ireland`

## Age

- Check if the value type is integer.
- The value `53` appears unusually high for a professional football player (commonly 16 <= Age <= 45) and may represent an outlier.

## ↓OVA

- Rename the column name to `OVA`
- Check if the value type is integer.

## POT

- Check if the value type is integer.

## Club

- Trim newline characters and spaces.
- Replace `No Club` with `<no_club>` (improves readability and makes filtering and category identification more explicit and consistent).

## Contract

- Mixed Data Formats
  - standard contract ranges: `2018 ~ 2024`
  - loan status records: `Jun 30, 2021 On Loan`
  - free agent status: `Free`
- Inconsistent Date Structures
  - year-only ranges: 2018 ~ 2024`
  - full calendar dates: `Jun 30, 2021 On Loan`
- Cleaning Step
  - Split contract range into start/end year
  - Extract loan status into separate column
  - Standardize date formats
  - Convert years to numeric/date types
  - Preserve `Free` as categorical status

Example:

| ContractStart | ContractEnd | LoadDateEnd | ContractType |
|---------------|-------------|-------------|--------------|
| 2018          | 2024        | NULL        | permanent    |
| NULL          | NULL        | 2021-06-30  | loan         |
| NULL          | NULL        | NULL        | free_agent   |


## Positions

- Multiple Values Stored in a Single Column
  - e.g., `RW, ST, CF`, `CAM, CM`
- Position Order Carries Meaning
  - This information is embedded implicitly. Should be preserved after cleaning.

Example:

| Position1 | Position2 | Position3 |
|-----------|-----------|-----------|
| RW        | ST        | CF        |
| CAM       | CM        | NULL      |
| GK        | NULL      | NULL      |

## Height

- Mixed Measurement Systems
  - metric format (cm): `170cm`
  - imperial format (feet ' inches " ): `6'2"`
- Heights Stored as Strings
- Cleaning Step
  - Convert all heights to a single measurement system (cm)
  - Remove unit symbols
  - Convert values to numeric type

Example:

| Original Height | HeightCM |
|-----------------|----------|
| 170cm           | 170      |
| 6'2"            | 188      |

## Weight

- Mixed Measurement Systems
  - metric values (kg): `72kg`
  - imperial values (lbs): `183lbs`
- Heights Stored as Strings
- Cleaning Step
  - Convert all heights to a single measurement system (kg)
  - Remove unit symbols
  - Convert values to numeric type

Example:

| Original Weight | WeightKG |
|-----------------|----------|
| 72kg            | 72       |
| 183lbs          | 83       |

## Preferred Foot

- Rename the column name to `PreferredFoot`

## BOV

- Check if the value type is integer.

## Best Position

- Delete (duplicated with `Position1` extracted from `Position`)

## Joined

- Convert string to date datatype
- Standardize date format
- Extract year/month if needed for analysis

## Loan Date End

- Delete (duplicated with `LoadDateEnd` extracted from `Contract`)

## Value

- Remove `€`  symbol
- Convert `M` and `K` to numeric values
- Standardize into one unit (million)
- Convert datatype to numeric
