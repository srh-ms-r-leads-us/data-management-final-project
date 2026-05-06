# Data Management Final Project Rules

## Branch Management

Since this repository will not contain a large amount of code, merge conflicts are expected to be infrequent. 
Each contributor should first create a branch named `dev_<owner>` (e.g., `dev_yang`), make changes on that branch, 
and then push to the `master` branch. If conflicts occur, resolve them within the `dev_<owner>` branch.

## Project Structure

- `data/`: Stores raw and processed datasets used in the Tableau project (e.g., CSV, Excel, extracts).
- `docs/`: Contains project documentation (e.g., docs, ppts), including data dictionaries, design notes, and analysis summaries.
- `flows/`: Includes Tableau Prep flow files (.tfl/.tflx) for data cleaning and transformation pipelines.
- `notebooks/`: Holds Jupyter Notebook files (.ipynb) for data exploring and visualization.
- `scripts/`: Holds supporting scripts (e.g., Python) for data preprocessing, validation, or automation.

## File Naming Rules

### Column Naming

- Lowercased words connected by underbars
- New column's name is old column's name + `'_cleaned'`
- If intermediate columns are needed, name them appropriately based on their purpose

### File Naming (for data / outputs)

- Pattern: <stage>_<col_range>.<ext>
- Example: output_col_01_15.csv

### Tableau Prep Flow Naming

- Pattern: flow_<col_range>.tfl
- Example: flow_col_01_15.tfl

### Jupyter Notebook File Naming

- Pattern: <stage>_<col_range>.ipynb
- Example: explore_col_01_15.ipynb

### Script Naming

- Pattern: <action>_<col_range>.py
- Example: clean_col_01_15.py, validate_col_16_30.py, explore_col_31_45.py, etc.
