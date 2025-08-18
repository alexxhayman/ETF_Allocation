import requests
import pandas as pd
import time
from datetime import datetime
import sys

class FMPDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
    def fetch_eurusd_historical_data(self, output_file="eurusd_data.csv", from_date="2010-01-01"):
        """
        Fetch all available EUR/USD historical data from FMP API
        """
        url = f"{self.base_url}/historical-price-full/EURUSD"
        params = {
            'apikey': self.api_key,
            'from': from_date  # Request data from specific date
        }
        
        try:
            print(f"Fetching EUR/USD historical data from {from_date} onwards...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we have historical data
            if 'historical' not in data:
                print("Error: No historical data found in response")
                print("Response:", data)
                return None
                
            historical_data = data['historical']
            print(f"Retrieved {len(historical_data)} data points")
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            
            # Reorder columns and clean up
            if not df.empty:
                # Standard FMP historical data columns
                expected_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                
                # Use available columns
                available_columns = [col for col in expected_columns if col in df.columns]
                df = df[available_columns]
                
                # Sort by date (newest first from API, so reverse for chronological order)
                df = df.sort_values('date', ascending=True)
                
                # Convert date to proper datetime format
                df['date'] = pd.to_datetime(df['date'])
                
                # Save to CSV
                df.to_csv(output_file, index=False)
                print(f"Data saved to {output_file}")
                
                # Display summary
                print(f"\nData Summary:")
                print(f"Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"Total records: {len(df)}")
                
                if 'close' in df.columns:
                    print(f"Latest EUR/USD rate: {df['close'].iloc[-1]:.5f}")
                
                print(f"\nFirst few rows:")
                print(df.head())
                
                return df
            else:
                print("No data retrieved")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except Exception as e:
            print(f"Error processing data: {e}")
            return None
    
    def fetch_eurusd_realtime(self):
        """
        Fetch current EUR/USD rate
        """
        url = f"{self.base_url}/quote/EURUSD"
        params = {
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                current_rate = data[0]
                print(f"Current EUR/USD: {current_rate.get('price', 'N/A')}")
                return current_rate
            else:
                print("No real-time data available")
                return None
                
        except Exception as e:
            print(f"Error fetching real-time data: {e}")
            return None

def main():
    # Get API key from user
    api_key = input("Enter your Financial Modeling Prep API key: ").strip()
    
    if not api_key:
        print("API key is required. Get one free at: https://financialmodelingprep.com/developer/docs")
        sys.exit(1)
    
    # Initialize fetcher
    fetcher = FMPDataFetcher(api_key)
    
    # Fetch current rate first
    print("Getting current EUR/USD rate...")
    fetcher.fetch_eurusd_realtime()
    
    print("\n" + "="*50)
    
    # Fetch historical data starting from 2010
    output_file = "eurusd_historical_data.csv"
    df = fetcher.fetch_eurusd_historical_data(output_file, from_date="2010-01-01")
    
    if df is not None:
        print(f"\n✅ Success! EUR/USD data saved to '{output_file}'")
        print(f"You can now open this file in Excel or use it for analysis")
    else:
        print("\n❌ Failed to fetch data. Please check your API key and try again.")

if __name__ == "__main__":
    main()