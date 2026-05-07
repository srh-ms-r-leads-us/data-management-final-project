# Cleaning Approach for the 21st to 40th Columns

## Wage
## Release Clause



- Removed the `€` symbol.
- Converted `M` and `K` suffixes into numeric values.
- Converted datatype to numeric.
- Preserved `0` values as valid records for players without wages.
- Preserved null values because some players do not have a release clause.


Example:

| Original Value | Cleaned Value |
|----------------|---------------|
| €105M          | 105000000     |
| €850K          | 850000        |
| €0             | 0            |

---


## Technical and Physical Attribute Validation

Validated columns:
- Attacking
- Crossing
- Finishing
- Heading Accuracy
- Short Passing
- Volleys
- Skill
- Dribbling
- Curve
- FK Accuracy
- Long Passing
- Ball Control
- Movement
- Acceleration
- Sprint Speed
- Agility
- Reactions
- Balance

Validation steps:
- Verified numeric datatype consistency.
- Checked for missing values.
- Checked for invalid ranges and formatting inconsistencies.
- Confirmed all values were within expected FIFA attribute ranges.
- Preserved aggregated statistics such as `Attacking`, `Skill`, and `Movement` because they represent combined player attributes.

No major cleaning was required.
