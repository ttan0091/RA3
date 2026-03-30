---
name: performing-eda
description: Conducts Exploratory Data Analysis (EDA) on datasets. Use when the user asks to "explore", "clean", or "visualize" a new CSV or dataset.
---

# Performing EDA (Exploratory Data Analysis)

## When to use this skill
- User uploads a `.csv` or `.json` file and asks "what's in here?".
- User wants to "check for missing values" or "see distributions".
- Debugging model performance by analyzing training data.

## Workflow
- [ ] **Load**: Read file into Pandas DataFrame.
- [ ] **Inspect Structure**: `df.info()`, `df.head()`, `df.describe()`.
- [ ] **Clean**: Handle missing values (`NaN`), duplicates, and incorrect types.
- [ ] **Univariate Analysis**: Histograms/Boxplots for single variables.
- [ ] **Bivariate Analysis**: Correlation matrix, Scatter plots for relationships.
- [ ] **Report**: Summarize findings (Outliers, Trends, Data Quality).

## Instructions

### 1. Standard Inspection Script (Python)
Use the `model` environment or a temporary script.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def quick_eda(filepath):
    df = pd.read_csv(filepath)
    print("--- INFO ---")
    print(df.info())
    print("\n--- DESCRIBE ---")
    print(df.describe())
    
    # Check nulls
    nulls = df.isnull().sum()
    if nulls.sum() > 0:
        print("\n--- NULLS ---")
        print(nulls[nulls > 0])
        
    return df
```

### 2. Visualization Standards
- Use **Seaborn** for statistical plots (nicer defaults than matplotlib).
- **Correlation Heatmap**: Critical for finding redundant features.
- **Pairplot**: Useful for small feature sets (< 10 features).

### 3. Notebooks vs Scripts
- Only create `.ipynb` files if the user *explicitly* asks for a notebook or "interactive exploration".
- Otherwise, write a `.py` script that outputs text summaries and saves plot images to a `plots/` folder.

## Resources
- [Pandas Cheatsheet](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf)
- [Seaborn Gallery](https://seaborn.pydata.org/examples/index.html)
