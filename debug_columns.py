import pandas as pd

# Load your ETF file and check column names
etf_file = "consolidated_etf_performance.csv"
etf_df = pd.read_csv(etf_file)

print("Column names in your CSV file:")
print("=" * 50)
for i, col in enumerate(etf_df.columns):
    print(f"{i}: '{col}'")

print(f"\nTotal columns: {len(etf_df.columns)}")

# Look for EUR ETF column variations
print("\nSearching for EUR ETF column...")
eur_columns = [col for col in etf_df.columns if 'EUR' in col and 'Europe' in col]
if eur_columns:
    print("Found EUR ETF columns:")
    for col in eur_columns:
        print(f"  - '{col}'")
else:
    print("No EUR ETF columns found. Looking for 'Europe' columns:")
    europe_columns = [col for col in etf_df.columns if 'Europe' in col]
    for col in europe_columns:
        print(f"  - '{col}'")