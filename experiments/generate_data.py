import zipfile
import pandas as pd
import os

# Path to your zip file
zip_path = "oesm23all.zip"  # Adjust this if your zip file has a different name

# Extract the contents of the zip file
# with zipfile.ZipFile(zip_path, "r") as zip_ref:
#     zip_ref.extractall("extracted_files")

# Path to the Excel file

file_name = 'all_data_M_2023.xlsx'
current_directory = os.path.dirname(__file__)

excel_file = os.path.join(
    current_directory, file_name
)

if os.path.exists(excel_file):
    # Read the Excel file
    df = pd.read_excel(excel_file)

    print(f"File successfully read: {excel_file}")
    print("\nDataFrame Info:")
    print(df.info())

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst Few Rows:")
    print(df.head())

    print("\nNumber of rows:", len(df))
    print("Number of columns:", len(df.columns))

    print("\nColumn Data Types:")
    print(df.dtypes)

    numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns
    if len(numeric_columns) > 0:
        print("\nBasic stats for numeric columns:")
        print(df[numeric_columns].describe())

    print("\nMissing values in each column:")
    print(df.isnull().sum())

    # Check for 'OCC_GROUP' column
    if "OCC_GROUP" in df.columns:
        print("\nUnique Values in 'OCC_GROUP':")
        print(df["OCC_GROUP"].unique())
    else:
        print("\n'OCC_GROUP' column not found in the dataset")

else:
    print(f"Excel file not found at {excel_file}")


import pandas as pd
import numpy as np


# Function to clean numeric columns
def clean_numeric(x):
    if isinstance(x, str):
        if x == "**" or x == "#":  # Add any other special characters you find
            return np.nan
        else:
            # Remove commas and percent signs if present
            return x.replace(",", "").replace("%", "")
    return x


# Apply the cleaning function to all columns
for col in df.columns:
    df[col] = df[col].apply(clean_numeric)

# Convert to numeric, coercing errors to NaN
for col in df.columns:
    if col not in [
        "AREA_TITLE",
        "PRIM_STATE",
        "NAICS",
        "NAICS_TITLE",
        "I_GROUP",
        "OCC_CODE",
        "OCC_TITLE",
        "O_GROUP",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Convert to Parquet
df.to_parquet("all_data_M_2023.parquet", index=False)

print("Data cleaned and saved to Parquet format.")
