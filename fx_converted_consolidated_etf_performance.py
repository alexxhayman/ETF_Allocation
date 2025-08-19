import pandas as pd
import numpy as np
from datetime import datetime

def convert_eur_etf_to_usd(etf_file, forex_file, output_file=None):
    """
    Create a new CSV with all original ETF data plus USD-converted EUR ETF values.
    
    Parameters:
    etf_file (str): Path to CSV file with ETF performance data
    forex_file (str): Path to CSV file with daily EUR/USD forex data
    output_file (str): Optional path for output CSV file
    
    Returns:
    pd.DataFrame: Complete DataFrame with all ETFs including USD conversion
    """
    
    # Load data
    print("Loading data files...")
    etf_df = pd.read_csv(etf_file)
    forex_df = pd.read_csv(forex_file)
    
    # Clean up column names by stripping spaces for both files
    etf_df.columns = etf_df.columns.str.strip()
    forex_df.columns = forex_df.columns.str.strip()
    
    # Create a copy of the original dataframe to work with
    result_df = etf_df.copy()
    
    # ETF column names (now cleaned)
    eur_etf_column = 'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-EUR-Acc'
    usd_etf_column = 'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-USD-Converted'
    
    # Add new USD column, initially copying EUR values
    result_df[eur_etf_column] = pd.to_numeric(result_df[eur_etf_column], errors='coerce')
    result_df[usd_etf_column] = result_df[eur_etf_column]
    
    # Convert forex date to datetime
    forex_df['date'] = pd.to_datetime(forex_df['date'])
    
    # Convert ETF date format (DD-MM-YYYY to datetime) for processing
    etf_df['Date_dt'] = pd.to_datetime(etf_df['Date'], format='%d-%m-%Y')
    
    # Convert EUR ETF column to numeric, handling any non-numeric values
    etf_df[eur_etf_column] = pd.to_numeric(etf_df[eur_etf_column], errors='coerce')
    
    # Filter for non-null EUR ETF data
    eur_data = etf_df[etf_df[eur_etf_column].notna()].copy()
    
    print(f"Found {len(eur_data)} EUR ETF data points to convert")
    
    # Track conversion results for analysis
    conversion_results = []
    
    for _, row in eur_data.iterrows():
        etf_date = row['Date_dt']
        eur_return = row[eur_etf_column] / 100  # Convert percentage to decimal
        
        # Get current month start and end dates
        current_month_start = etf_date.replace(day=1)
        if etf_date.month == 12:
            next_month_start = etf_date.replace(year=etf_date.year + 1, month=1, day=1)
        else:
            next_month_start = etf_date.replace(month=etf_date.month + 1, day=1)
        
        # Get previous month start
        if etf_date.month == 1:
            prev_month_start = etf_date.replace(year=etf_date.year - 1, month=12, day=1)
        else:
            prev_month_start = etf_date.replace(month=etf_date.month - 1, day=1)
        
        # Get forex rates for current month (last trading day)
        current_month_forex = forex_df[
            (forex_df['date'] >= current_month_start) & 
            (forex_df['date'] < next_month_start)
        ]
        
        # Get forex rates for previous month (last trading day)
        prev_month_forex = forex_df[
            (forex_df['date'] >= prev_month_start) & 
            (forex_df['date'] < current_month_start)
        ]
        
        if len(current_month_forex) > 0 and len(prev_month_forex) > 0:
            # Get month-end rates (last trading day)
            current_rate = current_month_forex['close'].iloc[-1]
            prev_rate = prev_month_forex['close'].iloc[-1]
            
            # Calculate forex change
            forex_change = current_rate / prev_rate
            
            # Convert EUR return to USD using multiplicative method
            usd_return = (1 + eur_return) * forex_change - 1
            
            # Update the USD column in the result dataframe
            mask = result_df['Date'] == row['Date']
            result_df.loc[mask, usd_etf_column] = round(usd_return * 100, 6)
            
            # Track for analysis
            conversion_results.append({
                'Date': row['Date'],
                'EUR_Return_Pct': round(eur_return * 100, 4),
                'USD_Return_Pct': round(usd_return * 100, 4),
                'Forex_Change_Pct': round((forex_change - 1) * 100, 4)
            })
    
    print(f"Successfully converted {len(conversion_results)} data points")
    
    # Display column information
    print(f"\nDataFrame now contains:")
    print(f"- Original EUR ETF column: '{eur_etf_column}'")
    print(f"- New USD ETF column: '{usd_etf_column}'")
    print(f"- All other ETF columns remain unchanged")
    
    # Create summary statistics from conversion results
    if conversion_results:
        conversion_df = pd.DataFrame(conversion_results)
        print("\nConversion Summary Statistics:")
        print(f"EUR Returns - Mean: {conversion_df['EUR_Return_Pct'].mean():.2f}%, Std: {conversion_df['EUR_Return_Pct'].std():.2f}%")
        print(f"USD Returns - Mean: {conversion_df['USD_Return_Pct'].mean():.2f}%, Std: {conversion_df['USD_Return_Pct'].std():.2f}%")
        print(f"Forex Impact - Mean: {conversion_df['Forex_Change_Pct'].mean():.2f}%, Std: {conversion_df['Forex_Change_Pct'].std():.2f}%")
    
    # Save to file if specified
    if output_file:
        result_df.to_csv(output_file, index=False)
        print(f"\nComplete dataset saved to: {output_file}")
    
    return result_df, pd.DataFrame(conversion_results) if conversion_results else None

def analyze_currency_impact(conversion_df):
    """
    Analyze the impact of currency conversion on returns.
    """
    if conversion_df is None or len(conversion_df) == 0:
        print("No conversion data available for analysis")
        return
        
    print("\nCurrency Impact Analysis:")
    print("=" * 50)
    
    # Calculate cumulative returns
    conversion_df['EUR_Cumulative'] = (1 + conversion_df['EUR_Return_Pct']/100).cumprod()
    conversion_df['USD_Cumulative'] = (1 + conversion_df['USD_Return_Pct']/100).cumprod()
    
    total_eur_return = (conversion_df['EUR_Cumulative'].iloc[-1] - 1) * 100
    total_usd_return = (conversion_df['USD_Cumulative'].iloc[-1] - 1) * 100
    currency_impact = total_usd_return - total_eur_return
    
    print(f"Total EUR Return: {total_eur_return:.2f}%")
    print(f"Total USD Return: {total_usd_return:.2f}%")
    print(f"Currency Impact: {currency_impact:.2f}%")
    
    # Periods where currency helped vs hurt
    helped = len(conversion_df[conversion_df['USD_Return_Pct'] > conversion_df['EUR_Return_Pct']])
    hurt = len(conversion_df[conversion_df['USD_Return_Pct'] < conversion_df['EUR_Return_Pct']])
    
    print(f"\nCurrency helped in {helped} periods ({helped/len(conversion_df)*100:.1f}%)")
    print(f"Currency hurt in {hurt} periods ({hurt/len(conversion_df)*100:.1f}%)")

# Example usage
if __name__ == "__main__":
    # File paths - these should match your current file structure
    etf_file = "consolidated_etf_performance.csv"  # Raw ETF data (input)
    forex_file = "eurusd_historical_data.csv"     # EUR/USD historical data
    output_file = "consolidated_etf_performance_with_usd.csv"  # USD-converted data (output)
    
    # Convert the data
    complete_df, conversion_df = convert_eur_etf_to_usd(etf_file, forex_file, output_file)
    
    # Analyze currency impact
    analyze_currency_impact(conversion_df)
    
    # Display sample of the complete dataset
    print("\nSample of Complete Dataset (showing EUR and USD columns):")
    eur_col = 'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-EUR-Acc'
    usd_col = 'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-USD-Converted'
    
    # Show rows where both EUR and USD have data
    sample_data = complete_df[complete_df[eur_col].notna()][['Date', eur_col, usd_col]].head(10)
    print(sample_data.to_string(index=False))
    
    print(f"\nDataset contains {len(complete_df)} total rows")
    print(f"EUR ETF has data for {complete_df[eur_col].notna().sum()} rows")
    print(f"USD ETF has converted data for {complete_df[usd_col].notna().sum()} rows")