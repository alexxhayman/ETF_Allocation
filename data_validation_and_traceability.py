"""
Data Validation and Traceability Script for ETF Allocation Project

This script validates the complete data pipeline and ensures traceability
from source Excel files to final allocation results.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import hashlib
import json

class DataValidator:
    """Comprehensive data validation and traceability for ETF allocation pipeline."""
    
    def __init__(self):
        self.validation_results = {}
        self.data_lineage = {}
        
    def calculate_file_checksum(self, file_path):
        """Calculate MD5 checksum for file integrity verification."""
        if not os.path.exists(file_path):
            return None
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def validate_source_files(self):
        """Validate all source data files exist and are accessible."""
        print("="*60)
        print("VALIDATING SOURCE FILES")
        print("="*60)
        
        # ETF Excel files
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
        
        # Economic data file
        economic_file = "Global Equity Fund (only economic data).xlsx"
        
        source_validation = {
            'etf_files': {},
            'economic_file': None
        }
        
        # Validate ETF files
        missing_etf_files = []
        for file in etf_files:
            if os.path.exists(file):
                checksum = self.calculate_file_checksum(file)
                size = os.path.getsize(file)
                modified = datetime.fromtimestamp(os.path.getmtime(file))
                
                source_validation['etf_files'][file] = {
                    'exists': True,
                    'checksum': checksum,
                    'size_bytes': size,
                    'last_modified': modified.isoformat()
                }
                print(f"OK {file} - ({size:,} bytes)")
            else:
                missing_etf_files.append(file)
                source_validation['etf_files'][file] = {'exists': False}
                print(f"❌ {file} - MISSING")
        
        # Validate economic file
        if os.path.exists(economic_file):
            checksum = self.calculate_file_checksum(economic_file)
            size = os.path.getsize(economic_file)
            modified = datetime.fromtimestamp(os.path.getmtime(economic_file))
            
            source_validation['economic_file'] = {
                'exists': True,
                'checksum': checksum,
                'size_bytes': size,
                'last_modified': modified.isoformat()
            }
            print(f"✅ {economic_file} - OK ({size:,} bytes)")
        else:
            source_validation['economic_file'] = {'exists': False}
            print(f"❌ {economic_file} - MISSING")
        
        self.validation_results['source_files'] = source_validation
        return len(missing_etf_files) == 0 and source_validation['economic_file']['exists']
    
    def validate_intermediate_files(self):
        """Validate intermediate processing files."""
        print("\\n" + "="*60)
        print("VALIDATING INTERMEDIATE FILES")
        print("="*60)
        
        intermediate_files = {
            'economic_data_extracted.csv': 'Economic data from Excel extraction',
            'dates_and_regimes.csv': 'Economic regime classifications',
            'consolidated_etf_performance.csv': 'Consolidated ETF performance data',
            'consolidated_etf_performance_with_usd.csv': 'USD-converted ETF data',
            'eurusd_historical_data.csv': 'EUR/USD exchange rate data'
        }
        
        intermediate_validation = {}
        
        for file, description in intermediate_files.items():
            if os.path.exists(file):
                try:
                    df = pd.read_csv(file)
                    checksum = self.calculate_file_checksum(file)
                    
                    intermediate_validation[file] = {
                        'exists': True,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'column_names': list(df.columns),
                        'checksum': checksum,
                        'description': description,
                        'date_range': self._get_date_range(df) if 'Date' in df.columns else None
                    }
                    print(f"✅ {file} - {len(df)} rows, {len(df.columns)} columns")
                    
                except Exception as e:
                    intermediate_validation[file] = {
                        'exists': True,
                        'error': str(e),
                        'description': description
                    }
                    print(f"⚠️  {file} - ERROR: {str(e)}")
            else:
                intermediate_validation[file] = {
                    'exists': False,
                    'description': description
                }
                print(f"❌ {file} - MISSING")
        
        self.validation_results['intermediate_files'] = intermediate_validation
        return intermediate_validation
    
    def _get_date_range(self, df):
        """Extract date range from dataframe."""
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            return {
                'start': df['Date'].min().isoformat() if not pd.isna(df['Date'].min()) else None,
                'end': df['Date'].max().isoformat() if not pd.isna(df['Date'].max()) else None,
                'count': df['Date'].notna().sum()
            }
        except:
            return None
    
    def validate_final_outputs(self):
        """Validate final allocation outputs."""
        print("\\n" + "="*60)
        print("VALIDATING FINAL OUTPUTS")
        print("="*60)
        
        final_files = {
            'optimal_etf_allocations_constrained.csv': 'Final allocation results',
            'ETF_Allocation_Summary_Report.md': 'Summary report',
            'Quick_Reference_Allocation_Table.csv': 'Quick reference table'
        }
        
        final_validation = {}
        
        for file, description in final_files.items():
            if os.path.exists(file):
                try:
                    if file.endswith('.csv'):
                        df = pd.read_csv(file)
                        final_validation[file] = {
                            'exists': True,
                            'rows': len(df),
                            'columns': len(df.columns),
                            'column_names': list(df.columns),
                            'description': description
                        }
                        print(f"✅ {file} - {len(df)} rows")
                        
                        # Special validation for allocation file
                        if 'optimal_etf_allocations_constrained' in file:
                            self._validate_allocation_constraints(df)
                    else:
                        size = os.path.getsize(file)
                        final_validation[file] = {
                            'exists': True,
                            'size_bytes': size,
                            'description': description
                        }
                        print(f"✅ {file} - {size:,} bytes")
                        
                except Exception as e:
                    final_validation[file] = {
                        'exists': True,
                        'error': str(e),
                        'description': description
                    }
                    print(f"⚠️  {file} - ERROR: {str(e)}")
            else:
                final_validation[file] = {
                    'exists': False,
                    'description': description
                }
                print(f"❌ {file} - MISSING")
        
        self.validation_results['final_outputs'] = final_validation
        return final_validation
    
    def _validate_allocation_constraints(self, df):
        """Validate allocation constraints (25% max, 100% total per regime)."""
        print("\\nValidating allocation constraints...")
        
        # Check max allocation constraint
        max_weight = df['Weight'].max()
        if max_weight > 0.25001:  # Small tolerance for rounding
            print(f"⚠️  WARNING: Max allocation {max_weight:.1%} exceeds 25% limit")
        else:
            print(f"✅ Max allocation constraint satisfied (max: {max_weight:.1%})")
        
        # Check portfolio totals
        portfolio_totals = df.groupby(['Period', 'Regime'])['Weight'].sum()
        
        invalid_portfolios = portfolio_totals[abs(portfolio_totals - 1.0) > 0.001]
        if len(invalid_portfolios) > 0:
            print("⚠️  WARNING: Portfolios with weights not summing to 100%:")
            for (period, regime), total in invalid_portfolios.items():
                print(f"    {period} - {regime}: {total:.1%}")
        else:
            print(f"✅ All {len(portfolio_totals)} portfolios sum to 100%")
        
        # Count regimes
        unique_regimes = df.groupby(['Period', 'Regime']).size()
        print(f"✅ Found {len(unique_regimes)} unique regime allocations")
        
        return {
            'max_allocation': max_weight,
            'portfolio_count': len(portfolio_totals),
            'invalid_portfolios': len(invalid_portfolios)
        }
    
    def trace_data_lineage(self):
        """Create complete data lineage documentation."""
        print("\\n" + "="*60)
        print("DATA LINEAGE TRACING")
        print("="*60)
        
        lineage = {
            'pipeline_steps': [
                {
                    'step': 1,
                    'name': 'Economic Data Extraction',
                    'input': 'Global Equity Fund (only economic data).xlsx',
                    'script': 'extract_economic_data.py',
                    'output': 'economic_data_extracted.csv',
                    'description': 'Extract GDP and PCE data from Excel'
                },
                {
                    'step': 2,
                    'name': 'Economic Regime Classification',
                    'input': 'economic_data_extracted.csv',
                    'script': 'regime_modelling.py',
                    'output': 'dates_and_regimes.csv',
                    'description': 'Classify economic periods into 4 regimes'
                },
                {
                    'step': 3,
                    'name': 'ETF Data Consolidation',
                    'input': '9 iShares Excel files',
                    'script': 'etf_extractor',
                    'output': 'consolidated_etf_performance.csv',
                    'description': 'Extract and consolidate ETF performance data'
                },
                {
                    'step': 4,
                    'name': 'Currency Conversion',
                    'input': 'consolidated_etf_performance.csv + eurusd_historical_data.csv',
                    'script': 'fx_converted_consolidated_etf_performance.py',
                    'output': 'consolidated_etf_performance_with_usd.csv',
                    'description': 'Convert EUR ETF returns to USD'
                },
                {
                    'step': 5,
                    'name': 'Portfolio Optimization',
                    'input': 'consolidated_etf_performance_with_usd.csv + dates_and_regimes.csv',
                    'script': 'optimal_allocation_refactored.py',
                    'output': 'optimal_etf_allocations_constrained.csv',
                    'description': 'Optimize allocations for each regime with 25% constraint'
                },
                {
                    'step': 6,
                    'name': 'Report Generation',
                    'input': 'optimal_etf_allocations_constrained.csv',
                    'script': 'Manual formatting',
                    'output': 'Summary reports and reference tables',
                    'description': 'Create stakeholder-friendly reports'
                }
            ],
            'validation_timestamp': datetime.now().isoformat(),
            'key_parameters': {
                'max_allocation_per_etf': '25%',
                'optimization_objective': 'Maximize Sharpe Ratio',
                'pre_garp_period': '2015-02-28 to 2020-01-31',
                'post_garp_period': '2020-02-29 to 2025-06-30',
                'economic_regimes': 4,
                'total_etfs': 9
            }
        }
        
        self.data_lineage = lineage
        
        print("Data lineage documented:")
        for step in lineage['pipeline_steps']:
            print(f"{step['step']}. {step['name']}")
            print(f"   Input: {step['input']}")
            print(f"   Script: {step['script']}")
            print(f"   Output: {step['output']}")
            print()
        
        return lineage
    
    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        print("\\n" + "="*60)
        print("GENERATING VALIDATION REPORT")
        print("="*60)
        
        # Combine all validation results
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'validation_results': self.validation_results,
            'data_lineage': self.data_lineage,
            'overall_status': 'PENDING'
        }
        
        # Determine overall status
        issues = []
        
        # Check source files
        if 'source_files' in self.validation_results:
            missing_etf = [f for f, data in self.validation_results['source_files']['etf_files'].items() 
                          if not data['exists']]
            if missing_etf:
                issues.append(f"Missing ETF files: {missing_etf}")
            
            if not self.validation_results['source_files']['economic_file']['exists']:
                issues.append("Missing economic data file")
        
        # Check intermediate files
        if 'intermediate_files' in self.validation_results:
            missing_intermediate = [f for f, data in self.validation_results['intermediate_files'].items() 
                                  if not data['exists']]
            if missing_intermediate:
                issues.append(f"Missing intermediate files: {missing_intermediate}")
        
        # Set overall status
        if len(issues) == 0:
            report['overall_status'] = 'PASSED'
            print("✅ OVERALL STATUS: PASSED")
        else:
            report['overall_status'] = 'FAILED'
            print("❌ OVERALL STATUS: FAILED")
            print("\\nIssues found:")
            for issue in issues:
                print(f"  - {issue}")
        
        # Save report
        with open('data_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\\nValidation report saved to: data_validation_report.json")
        return report
    
    def run_complete_validation(self):
        """Run complete data validation and traceability analysis."""
        print("STARTING COMPLETE DATA VALIDATION")
        print("="*60)
        
        # Run all validation steps
        self.validate_source_files()
        self.validate_intermediate_files()
        self.validate_final_outputs()
        self.trace_data_lineage()
        
        # Generate final report
        report = self.generate_validation_report()
        
        print("\\nVALIDATION COMPLETE")
        return report


def main():
    """Run the complete validation process."""
    validator = DataValidator()
    report = validator.run_complete_validation()
    return report


if __name__ == "__main__":
    main()