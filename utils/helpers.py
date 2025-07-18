import numpy as np
import pandas as pd
import re

def extract_full_and_half(value):
    if pd.isna(value):
        return np.nan, np.nan
    try:
        value = value.strip()
        if '+' in value:
            parts = value.split('+')
            full = int(parts[0].strip()) if parts[0].strip().isdigit() else 0
            half = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 0
            return full, half
        else:
            return int(value), 0
    except ValueError:
        return np.nan, np.nan


def convert_mixed_number(value):
    if pd.isna(value):
        return np.nan
    try:
        if '+' in value:
            parts = value.split('+')
            return sum(int(part.strip()) for part in parts if part.strip().isdigit())
        return int(value)
    except ValueError:
        return np.nan


def parse_sqft_range(sqft_str):
    if pd.isna(sqft_str):
        return None

    sqft_str = sqft_str.replace(",", "").strip()

    # Case 1: It's a range like "500-599"
    match = re.match(r"^(\d+)-(\d+)$", sqft_str)
    if match:
        low, high = map(float, match.groups())
        return round((low + high) / 2)

    # Case 2: It's a single numeric value like "1043"
    if sqft_str.isdigit():
        return int(sqft_str)

    # Otherwise invalid or unexpected format
    return None