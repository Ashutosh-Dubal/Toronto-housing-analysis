import pandas as pd
import numpy as np
import re
from utils.helpers import convert_mixed_number
from utils.helpers import parse_sqft_range

# --- Validation Functions ---
def is_valid_beds(val):
    return pd.isna(val) or bool(re.match(r"^\d+(\+\d+)?$", str(val).strip()))

def is_valid_baths(val):
    return pd.isna(val) or bool(re.match(r"^\d+(\+\d+)?$", str(val).strip()))

def is_valid_sqft(val):
    val = str(val).replace(",", "").strip()
    return pd.isna(val) or bool(re.match(r"^\d+$", val) or re.match(r"^\d+-\d+$", val))

df = pd.read_csv('../Housing_Price_Analysis/data/raw/toronto_housing_data.csv')
print(df.info())
print("------------------")
print(df.isnull().sum())

# Replace missing indicators with NaN
missing_values = ["-", "—", "–", ""]
df.replace(missing_values, np.nan, inplace=True)

# Replace words bed, bath and sqft
df['beds'] = df['beds'].str.replace("bed", "", regex=False)
df['baths'] = df['baths'].str.replace("bath", "", regex=False)
df['sqft'] = df['sqft'].str.replace("sqft", "", regex=False)

# Drop rows where more than 1 key feature is missing
df["missing_count"] = df[["beds", "baths", "sqft"]].isna().sum(axis=1)
df = df[df["missing_count"] <= 1].drop(columns=["missing_count"])

# Drop rows with invalid values in key fields
print("Before filtering:", len(df))
valid_beds = df["beds"].apply(is_valid_beds)
valid_baths = df["baths"].apply(is_valid_baths)
valid_sqft = df["sqft"].apply(is_valid_sqft)
print("Valid beds count:", valid_beds.sum())
print("Valid baths count:", valid_baths.sum())
print("Valid sqft count:", valid_sqft.sum())

df = df[valid_beds & valid_baths & valid_sqft]
print("After filtering:", len(df))

# Trimming the extra whitespace
df['beds'] = df['beds'].str.strip()
df['baths'] = df['baths'].str.strip()
df['sqft'] = df['sqft'].str.strip()

# Dropping rows where all data is missing
df.dropna(subset=['beds', 'baths', 'sqft'], how='all', inplace=True)

# Creating TotalBeds and TotalBaths columns
df['TotalBeds'] = df['beds'].apply(convert_mixed_number)
df['TotalBaths'] = df['baths'].apply(convert_mixed_number)
df['CleanedSqft'] = df['sqft'].apply(parse_sqft_range)

print(df.head(20))

print("------------------")
print(len(df))
print(df.isnull().sum())

print("Saving clean data")
df.to_csv("../Housing_Price_Analysis/data/clean/toronto_housing_data.csv", index=False)