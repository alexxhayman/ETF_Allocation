import pandas as pd
import os

def extract_economic_data(excel_file_path, output_csv_path):
    """
    Extract GDP QoQ and PCE Prices data from Excel file and save to CSV.
    
    Parameters:
    excel_file_path (str): Path to the Excel file
    output_csv_path (str): Path for the output CSV file
    """
    
    try:
        # Read the Excel file, specific sheet "Eco Data"
        # Skip first 2 rows (headers) and start from row 3 (index 2)
        df = pd.read_excel(
            excel_file_path, 
            sheet_name="Eco Data",
            skiprows=2,  # Skip rows 1 and 2
            usecols=[0, 5, 7],  # Column A (dates), F (GDP), H (PCE) - 0-indexed
            names=['Date', 'US_GDP_QoQ_Ann', 'PCE_Prices']  # Rename columns
        )
        
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        # Convert percentage strings to floats if needed
        for col in ['US_GDP_QoQ_Ann', 'PCE_Prices']:
            if df[col].dtype == 'object':
                # Remove % sign and convert to float
                df[col] = df[col].astype(str).str.replace('%', '').astype(float)
        
        # Save to CSV
        df.to_csv(output_csv_path, index=False)
        
        print(f"✅ Data extracted successfully!")
        print(f"📁 Output saved to: {output_csv_path}")
        print(f"📊 Rows extracted: {len(df)}")
        print(f"\nFirst 5 rows preview:")
        print(df.head())
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Error: Excel file not found at {excel_file_path}")
    except ValueError as e:
        print(f"❌ Error reading Excel file: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

# Usage example
if __name__ == "__main__":
    # Update these paths to match your file locations
    excel_file = "Global Equity Fund (only economic data).xlsx"  # Your Excel file name
    csv_output = "economic_data_extracted.csv"  # Output CSV file name
    
    # Extract the data
    extracted_data = extract_economic_data(excel_file, csv_output)