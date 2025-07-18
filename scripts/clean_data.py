import pandas as pd
import numpy as np
import re
import logging
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.helpers import convert_mixed_number, parse_sqft_range, extract_full_and_half

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Configurable paths ---
RAW_DATA_PATH = Path("data/raw/toronto_housing_data.csv")
CLEAN_DATA_PATH = Path("data/clean/toronto_housing_data.csv")

# --- Validation Functions ---
def is_valid_beds(val):
    return pd.isna(val) or bool(re.match(r"^\d+(\+\d+)?$", str(val).strip()))

def is_valid_baths(val):
    return pd.isna(val) or bool(re.match(r"^\d+(\+\d+)?$", str(val).strip()))

def is_valid_sqft(val):
    val = str(val).replace(",", "").strip()
    return pd.isna(val) or bool(re.match(r"^\d+$", val) or re.match(r"^\d+-\d+$", val))

def main():
    # --- Check if raw data exists ---
    if not RAW_DATA_PATH.exists():
        logging.error(f"Raw data not found at: {RAW_DATA_PATH}")
        return

    # --- Load raw data ---
    logging.info("Loading raw housing data...")
    df = pd.read_csv(RAW_DATA_PATH)
    logging.info(f"Initial rows: {len(df)}")
    logging.info(f"Missing values:\n{df.isnull().sum()}")

    # --- Clean and standardize ---
    missing_values = ["-", "—", "–", ""]
    df.replace(missing_values, np.nan, inplace=True)

    df['beds'] = df['beds'].str.replace("bed", "", regex=False)
    df['baths'] = df['baths'].str.replace("bath", "", regex=False)
    df['sqft'] = df['sqft'].str.replace("sqft", "", regex=False)

    # --- Drop rows where more than 1 of the key fields are missing ---
    df["missing_count"] = df[["beds", "baths", "sqft"]].isna().sum(axis=1)
    df = df[df["missing_count"] <= 1].drop(columns=["missing_count"])

    # --- Validate data format ---
    valid_beds = df["beds"].apply(is_valid_beds)
    valid_baths = df["baths"].apply(is_valid_baths)
    valid_sqft = df["sqft"].apply(is_valid_sqft)

    df = df[valid_beds & valid_baths & valid_sqft]
    logging.info(f"Rows after validation: {len(df)}")

    # --- Clean formatting ---
    df['beds'] = df['beds'].str.strip()
    df['baths'] = df['baths'].str.strip()
    df['sqft'] = df['sqft'].str.strip()

    # --- Drop rows missing all three ---
    df.dropna(subset=['beds', 'baths', 'sqft'], how='all', inplace=True)

    # --- Feature Engineering ---
    df['TotalBeds'] = df['beds'].apply(convert_mixed_number)
    df['TotalBaths'] = df['baths'].apply(convert_mixed_number)
    df['CleanedSqft'] = df['sqft'].apply(parse_sqft_range)
    df[['full_bed', 'half_bed']] = df['beds'].apply(lambda x: pd.Series(extract_full_and_half(x)))

    # --- Final Cleaning ---
    df.drop_duplicates(inplace=True)

    # Convert to numeric
    df["TotalBeds"] = df["TotalBeds"].astype(float)
    df["TotalBaths"] = df["TotalBaths"].astype(float)
    df["CleanedSqft"] = df["CleanedSqft"].astype(float)

    # --- Save Clean Data ---
    CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DATA_PATH, index=False)

    logging.info(f"✅ Saved cleaned dataset with {len(df)} rows to: {CLEAN_DATA_PATH}")
    logging.info(f"Final column null counts:\n{df.isnull().sum()}")

if __name__ == "__main__":
    main()