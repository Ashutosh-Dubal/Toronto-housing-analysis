import numpy as np
import pandas as pd
import re

def clean_detail(text):
    """Cleans and converts price string to integer."""
    text = text.strip().lower()
    if text == '–' or text == '':
        return None
    return text.lower().replace('bed', '').replace('bath', '').replace('sqft', '')

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