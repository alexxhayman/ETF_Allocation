import pandas as pd
import numpy as np
from datetime import datetime

def convert_eur_etf_to_usd(etf_file, forex_file, output_file=None):
    """
    Convert EUR-denominated ETF performance to USD using monthly forex changes.
    
    Parameters:
    etf_file (str): Path to CSV file with ETF performance data
    forex_file (str): Path to CSV file with daily EUR/USD forex data
    output_file (str): Optional path for output CSV file
    
    Returns:
    pd.DataFrame: DataFrame with converted USD performance
    """
    
    # Load data
    print("Loading data files...")
    etf_df = pd.read_csv(etf_file)
    forex_df = pd.read_csv(forex_file)
    
    # ETF column name for the EUR fund
    eur_etf_column = 'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-EUR-Acc'
    
    # Convert forex date to datetime
    forex_df['date'] = pd.to_datetime(forex_df['date'])
    
    # Convert ETF date format (DD-MM-YYYY to datetime)
    etf_df['Date'] = pd.to_datetime(etf_df['Date'], format='%d-%m-%Y')
    
    # Filter for non-null EUR ETF data
    eur_data = etf_df[etf_df[eur_etf_column].notna()].copy()
    
    print(f"Found {len(eur_data)} EUR ETF data points to convert")
    
    # Prepare results list
    results = []
    
    for _, row in eur_data.iterrows():
        etf_date = row['Date']
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
            
            results.append({
                'Date': etf_date.strftime('%Y-%m-%d'),
                'EUR_Return_Pct': round(eur_return * 100, 4),
                'USD_Return_Pct': round(usd_return * 100, 4),
                'Forex_Start_Rate': round(prev_rate, 5),
                'Forex_End_Rate': round(current_rate, 5),
                'Forex_Change_Pct': round((forex_change - 1) * 100, 4)
            })
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    print(f"Successfully converted {len(results_df)} data points")
    
    # Display summary statistics
    print("\nSummary Statistics:")
    print(f"EUR Returns - Mean: {results_df['EUR_Return_Pct'].mean():.2f}%, Std: {results_df['EUR_Return_Pct'].std():.2f}%")
    print(f"USD Returns - Mean: {results_df['USD_Return_Pct'].mean():.2f}%, Std: {results_df['USD_Return_Pct'].std():.2f}%")
    print(f"Forex Impact - Mean: {results_df['Forex_Change_Pct'].mean():.2f}%, Std: {results_df['Forex_Change_Pct'].std():.2f}%")
    
    # Save to file if specified
    if output_file:
        results_df.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
    
    return results_df

def analyze_currency_impact(results_df):
    """
    Analyze the impact of currency conversion on returns.
    """
    print("\nCurrency Impact Analysis:")
    print("=" * 50)
    
    # Calculate cumulative returns
    results_df['EUR_Cumulative'] = (1 + results_df['EUR_Return_Pct']/100).cumprod()
    results_df['USD_Cumulative'] = (1 + results_df['USD_Return_Pct']/100).cumprod()
    
    total_eur_return = (results_df['EUR_Cumulative'].iloc[-1] - 1) * 100
    total_usd_return = (results_df['USD_Cumulative'].iloc[-1] - 1) * 100
    currency_impact = total_usd_return - total_eur_return
    
    print(f"Total EUR Return: {total_eur_return:.2f}%")
    print(f"Total USD Return: {total_usd_return:.2f}%")
    print(f"Currency Impact: {currency_impact:.2f}%")
    
    # Periods where currency helped vs hurt
    helped = len(results_df[results_df['USD_Return_Pct'] > results_df['EUR_Return_Pct']])
    hurt = len(results_df[results_df['USD_Return_Pct'] < results_df['EUR_Return_Pct']])
    
    print(f"\nCurrency helped in {helped} periods ({helped/len(results_df)*100:.1f}%)")
    print(f"Currency hurt in {hurt} periods ({hurt/len(results_df)*100:.1f}%)")

# Example usage
if __name__ == "__main__":
    # File paths - update these to match your file locations
    etf_file = "consolidated_etf_performance.csv"
    forex_file = "eurusd_historical_data.csv"
    output_file = "eur_etf_usd_converted.csv"
    
    # Convert the data
    results_df = convert_eur_etf_to_usd(etf_file, forex_file, output_file)
    
    # Analyze currency impact
    analyze_currency_impact(results_df)
    
    # Display first few results
    print("\nFirst 10 Converted Results:")
    print(results_df.head(10).to_string(index=False))
    
    # Display recent results
    print("\nMost Recent 5 Results:")
    print(results_df.tail(5).to_string(index=False))