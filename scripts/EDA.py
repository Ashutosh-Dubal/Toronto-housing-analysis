import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import argparse
import json

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Toronto Housing EDA Script")
parser.add_argument('--input', type=str, default='../Toronto-housing-analysis/data/clean/toronto_housing_data.csv', help='Path to cleaned CSV')
parser.add_argument('--output_dir', type=str, default='./eda_outputs', help='Directory to save output plots and summary')
args = parser.parse_args()

# --- Setup ---
sns.set(style="whitegrid")
data_path = Path(args.input)
output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)

# --- Load Data ---
df = pd.read_csv(data_path)

# --- Summary Statistics ---
summary_stats = df.describe().to_dict()
with open(output_dir / 'summary_stats.json', 'w') as f:
    json.dump(summary_stats, f, indent=2)

# --- Correlation ---
features = ['price', 'TotalBeds', 'TotalBaths', 'CleanedSqft', 'full_bed', 'half_bed']
corr_matrix = df[features].corr()
df['log_price'] = np.log1p(df['price'])

# --- Save Plots ---
plt.figure(figsize=(8, 5))
sns.histplot(df['log_price'], kde=True)
plt.title("Log-Transformed Price Distribution")
plt.xlabel("log(price + 1)")
plt.tight_layout()
plt.savefig(output_dir / "log_price_distribution.png")
plt.close()

plt.figure(figsize=(6, 4))
sns.scatterplot(data=df, x='TotalBeds', y='price')
plt.title("Price vs. Number of Bedrooms")
plt.tight_layout()
plt.savefig(output_dir / "price_vs_beds.png")
plt.close()

sns.pairplot(df[features])
plt.suptitle("Pairplot of Price, Beds, Baths, and Sqft", y=1.02)
plt.savefig(output_dir / "pairplot_features.png")
plt.close()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(output_dir / "correlation_heatmap.png")
plt.close()

# --- Group Avg Plots ---
def plot_group_avg(df, group_col, color):
    avg_price = df.groupby(group_col)["price"].mean() / 1_000_000
    avg_price.plot(kind='bar', color=color)
    plt.title(f"Average Price by {group_col}")
    plt.ylabel("Average Price (Million CAD)")
    plt.tight_layout()
    plt.savefig(output_dir / f"avg_price_by_{group_col.lower()}.png")
    plt.close()
    return avg_price

bed_avg = plot_group_avg(df, 'TotalBeds', 'skyblue')
bath_avg = plot_group_avg(df, 'TotalBaths', 'lightgreen')

# --- Sqft Line Plot ---
sqft_avg = df.groupby("CleanedSqft")["price"].mean().sort_index() / 1_000_000
sqft_avg.plot(marker='o')
plt.title("Average Price by Square Footage")
plt.ylabel("Average Price (Million CAD)")
plt.tight_layout()
plt.savefig(output_dir / "avg_price_by_sqft.png")
plt.close()

# --- Rolling Averages ---
def plot_rolling(avg_series, label, color):
    avg_series.rolling(window=5, min_periods=1).mean().plot(
        kind='line', linestyle='--', color=color)
    plt.title(f"Rolling Avg Price by {label}")
    plt.ylabel("Avg Price (Million CAD, Rolling Avg)")
    plt.tight_layout()
    plt.savefig(output_dir / f"rolling_avg_price_by_{label.lower()}.png")
    plt.close()

plot_rolling(sqft_avg, "Sqft", "orange")
plot_rolling(bed_avg, "Bedrooms", "blue")
plot_rolling(bath_avg, "Bathrooms", "green")

# --- Sqft Range Distribution ---
sqft_bins = [0, 499, 999, 1499, 1999, 2499, 2999, 3499, 3999, 4499, 4999, float('inf')]
sqft_labels = ['0–499', '500–999', '1000–1499', '1500–1999', '2000–2499',
               '2500–2999', '3000–3499', '3500–3999', '4000–4499', '4500–4999', '5000+']
df['sqft_range'] = pd.cut(df['CleanedSqft'], bins=sqft_bins, labels=sqft_labels)

range_counts = df['sqft_range'].value_counts().sort_index()
range_counts.to_csv(output_dir / 'sqft_range_distribution.csv')