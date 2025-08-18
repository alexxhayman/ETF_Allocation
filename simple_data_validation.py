"""
Simple Data Validation for ETF Allocation Project
"""

import pandas as pd
import os
from datetime import datetime

def validate_pipeline():
    """Simple validation of the complete data pipeline."""
    
    print("="*60)
    print("ETF ALLOCATION PROJECT - DATA VALIDATION")
    print("="*60)
    
    # Check source files
    print("\n1. SOURCE FILES:")
    print("-" * 30)
    
    etf_files = [
        "iShares-Core-Dividend-Growth-ETF_fund.xlsx",
        "iShares-MSCI-USA-Momentum-Factor-ETF_fund.xlsx", 
        "iShares-SP-500-Value-ETF_fund.xlsx",
        "iShares-Asia-50-ETF_fund.xlsx",
        "iShares-MSCI-USA-Quality-GARP-ETF_fund.xlsx",
        "iShares-MSCI-EAFE-Min-Vol-Factor-ETF_fund.xlsx",
        "iShares-Edge-MSCI-World-Momentum-Factor-UCITS-ETF-USD-Acc_fund.xlsx",
        "iShares-MSCI-USA-Min-Vol-Factor-ETF_fund.xlsx",
        "iShares-Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-EUR-Acc_fund.xlsx"
    ]
    
    economic_file = "Global Equity Fund (only economic data).xlsx"
    
    etf_count = 0
    for file in etf_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"[OK] {file} ({size:,} bytes)")
            etf_count += 1
        else:
            print(f"[MISSING] {file}")
    
    if os.path.exists(economic_file):
        size = os.path.getsize(economic_file)
        print(f"[OK] {economic_file} ({size:,} bytes)")
        eco_exists = True
    else:
        print(f"[MISSING] {economic_file}")
        eco_exists = False
    
    print(f"\nETF Files Found: {etf_count}/9")
    print(f"Economic File: {'YES' if eco_exists else 'NO'}")
    
    # Check intermediate files
    print("\n2. INTERMEDIATE FILES:")
    print("-" * 30)
    
    intermediate_files = {
        'economic_data_extracted.csv': 'Economic data extraction',
        'dates_and_regimes.csv': 'Economic regime classification',
        'consolidated_etf_performance.csv': 'Consolidated ETF data',
        'consolidated_etf_performance_with_usd.csv': 'USD-converted ETF data',
    }
    
    intermediate_status = {}
    
    for file, description in intermediate_files.items():
        if os.path.exists(file):
            try:
                df = pd.read_csv(file)
                print(f"[OK] {file} - {len(df)} rows, {len(df.columns)} columns")
                intermediate_status[file] = True
            except Exception as e:
                print(f"[ERROR] {file} - Cannot read: {str(e)}")
                intermediate_status[file] = False
        else:
            print(f"[MISSING] {file}")
            intermediate_status[file] = False
    
    # Check final outputs
    print("\n3. FINAL OUTPUTS:")
    print("-" * 30)
    
    final_files = [
        'optimal_etf_allocations_constrained.csv',
        'ETF_Allocation_Summary_Report.md',
        'Quick_Reference_Allocation_Table.csv'
    ]
    
    final_status = {}
    
    for file in final_files:
        if os.path.exists(file):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(file)
                    print(f"[OK] {file} - {len(df)} rows")
                    final_status[file] = True
                except Exception as e:
                    print(f"[ERROR] {file} - {str(e)}")
                    final_status[file] = False
            else:
                size = os.path.getsize(file)
                print(f"[OK] {file} - {size:,} bytes")
                final_status[file] = True
        else:
            print(f"[MISSING] {file}")
            final_status[file] = False
    
    # Validate allocation constraints
    print("\n4. ALLOCATION VALIDATION:")
    print("-" * 30)
    
    if final_status.get('optimal_etf_allocations_constrained.csv', False):
        try:
            df = pd.read_csv('optimal_etf_allocations_constrained.csv')
            
            # Check max allocation
            max_weight = df['Weight'].max()
            print(f"Maximum allocation: {max_weight:.1%}")
            if max_weight <= 0.25001:
                print("[OK] 25% constraint satisfied")
            else:
                print("[WARNING] 25% constraint VIOLATED")
            
            # Check portfolio totals
            portfolio_totals = df.groupby(['Period', 'Regime'])['Weight'].sum()
            invalid_count = sum(abs(total - 1.0) > 0.001 for total in portfolio_totals)
            
            print(f"Portfolio count: {len(portfolio_totals)}")
            if invalid_count == 0:
                print("[OK] All portfolios sum to 100%")
            else:
                print(f"[WARNING] {invalid_count} portfolios don't sum to 100%")
            
            # Check expected 8 allocations
            if len(portfolio_totals) == 8:
                print("[OK] Expected 8 regime allocations found")
            else:
                print(f"[WARNING] Expected 8 allocations, found {len(portfolio_totals)}")
                
        except Exception as e:
            print(f"[ERROR] Cannot validate allocations: {str(e)}")
    
    # Summary
    print("\n5. PIPELINE SUMMARY:")
    print("-" * 30)
    
    etf_complete = etf_count == 9
    eco_complete = eco_exists
    intermediate_complete = all(intermediate_status.values())
    final_complete = all(final_status.values())
    
    print(f"Source Data Complete: {'YES' if etf_complete and eco_complete else 'NO'}")
    print(f"Intermediate Processing: {'YES' if intermediate_complete else 'NO'}")
    print(f"Final Outputs: {'YES' if final_complete else 'NO'}")
    
    overall_status = etf_complete and eco_complete and intermediate_complete and final_complete
    
    print(f"\nOVERALL PIPELINE STATUS: {'COMPLETE' if overall_status else 'INCOMPLETE'}")
    
    # Data lineage summary
    print("\n6. DATA LINEAGE SUMMARY:")
    print("-" * 30)
    
    lineage_steps = [
        "Excel Sources -> extract_economic_data.py -> economic_data_extracted.csv",
        "economic_data_extracted.csv -> regime_modelling.py -> dates_and_regimes.csv", 
        "Excel Sources -> etf_extractor -> consolidated_etf_performance.csv",
        "consolidated_etf_performance.csv -> fx_converter -> consolidated_etf_performance_with_usd.csv",
        "USD ETF data + regimes -> optimal_allocation_refactored.py -> final results"
    ]
    
    for i, step in enumerate(lineage_steps, 1):
        print(f"{i}. {step}")
    
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    
    return overall_status

if __name__ == "__main__":
    validate_pipeline()