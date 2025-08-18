import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class ETFRegimeOptimizer:
    """
    ETF portfolio optimizer that creates regime-specific allocations.
    
    Features:
    - Maximum 25% allocation per ETF
    - Optimizes Sharpe ratio for each economic regime
    - Handles pre/post GARP periods separately
    """
    
    def __init__(self, etf_data_path, regime_data_path, max_allocation=0.25):
        self.etf_data_path = etf_data_path
        self.regime_data_path = regime_data_path
        self.max_allocation = max_allocation
        self.etf_data = None
        self.regime_data = None
        self.merged_data = None
        self.pre_garp_data = None
        self.post_garp_data = None
        
        # ETF name mapping for cleaner output
        self.etf_name_map = {
            'Core-Dividend-Growth-ETF': 'Dividend_Growth',
            'MSCI-USA-Momentum-Factor-ETF': 'USA_Momentum', 
            'SP-500-Value-ETF': 'SP500_Value',
            'Asia-50-ETF': 'Asia_50',
            'MSCI-USA-Quality-GARP-ETF': 'USA_GARP',
            'MSCI-EAFE-Min-Vol-Factor-ETF': 'EAFE_MinVol',
            'Edge-MSCI-World-Momentum-Factor-UCITS-ETF-USD-Acc': 'World_Momentum',
            'MSCI-USA-Min-Vol-Factor-ETF': 'USA_MinVol',
            'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-EUR-Acc': 'Europe_Momentum_EUR',
            'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-USD-Converted': 'Europe_Momentum_USD'
        }
        
    def load_data(self):
        """Load and clean both ETF and regime data."""
        print("="*60)
        print("LOADING DATA")
        print("="*60)
        
        # Load ETF data
        print("Loading ETF performance data...")
        self.etf_data = pd.read_csv(self.etf_data_path)
        
        # Clean column names
        self.etf_data.columns = self.etf_data.columns.str.strip()
        
        # Find date column
        date_col = self._find_date_column(self.etf_data)
        if date_col != 'Date':
            self.etf_data = self.etf_data.rename(columns={date_col: 'Date'})
        
        # Rename ETF columns
        self.etf_data = self.etf_data.rename(columns=self.etf_name_map)
        
        # Parse dates and convert percentages
        self.etf_data['Date'] = pd.to_datetime(self.etf_data['Date'], format='%d-%m-%Y')
        self._convert_percentage_columns(self.etf_data)
        
        # Load regime data
        print("Loading economic regime data...")
        self.regime_data = pd.read_csv(self.regime_data_path)
        self.regime_data['Date'] = pd.to_datetime(self.regime_data['Date'], format='%Y-%m-%d')
        
        print(f"Loaded {len(self.etf_data)} ETF observations and {len(self.regime_data)} regime classifications")
        
    def _find_date_column(self, df):
        """Find the date column in the dataframe."""
        for col in df.columns:
            if col.lower().strip() in ['date', 'dates']:
                return col
        return df.columns[0]  # Default to first column
    
    def _convert_percentage_columns(self, df):
        """Convert percentage strings to numeric values."""
        etf_cols = [col for col in df.columns if col != 'Date']
        for col in etf_cols:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%', ''), errors='coerce')
    
    def merge_data(self):
        """Merge ETF and regime data using year-month matching."""
        print("\nMerging datasets...")
        
        # Create year-month keys for matching
        self.etf_data['YearMonth'] = self.etf_data['Date'].dt.to_period('M')
        self.regime_data['YearMonth'] = self.regime_data['Date'].dt.to_period('M')
        
        # Merge on year-month
        self.merged_data = pd.merge(
            self.etf_data, 
            self.regime_data[['YearMonth', 'Regime']], 
            on='YearMonth', 
            how='inner'
        )
        
        # Clean up
        self.merged_data = self.merged_data.drop('YearMonth', axis=1).sort_values('Date').reset_index(drop=True)
        
        if len(self.merged_data) == 0:
            raise ValueError("No matching dates found between datasets")
        
        print(f"Successfully merged: {len(self.merged_data)} observations")
        print(f"Date range: {self.merged_data['Date'].min().strftime('%Y-%m-%d')} to {self.merged_data['Date'].max().strftime('%Y-%m-%d')}")
        
    def split_periods(self):
        """Split data into pre-GARP and post-GARP periods."""
        print("\nSplitting into analysis periods...")
        
        start_date = pd.to_datetime('2015-02-28')
        garp_date = pd.to_datetime('2020-02-29')
        
        # Pre-GARP period (exclude USA_GARP)
        pre_mask = (self.merged_data['Date'] >= start_date) & (self.merged_data['Date'] < garp_date)
        self.pre_garp_data = self.merged_data[pre_mask].copy()
        
        # Exclude GARP column
        pre_cols = [col for col in self.pre_garp_data.columns if col != 'USA_GARP']
        self.pre_garp_data = self.pre_garp_data[pre_cols]
        
        # Post-GARP period (include all ETFs)
        post_mask = self.merged_data['Date'] >= garp_date
        self.post_garp_data = self.merged_data[post_mask].copy()
        
        print(f"Pre-GARP: {len(self.pre_garp_data)} observations ({self.pre_garp_data['Date'].min().strftime('%Y-%m-%d')} to {self.pre_garp_data['Date'].max().strftime('%Y-%m-%d')})")
        print(f"Post-GARP: {len(self.post_garp_data)} observations ({self.post_garp_data['Date'].min().strftime('%Y-%m-%d')} to {self.post_garp_data['Date'].max().strftime('%Y-%m-%d')})")
        
    def optimize_portfolio(self, data, regime=None, min_observations=5):
        """
        Optimize portfolio for maximum Sharpe ratio with constraints.
        
        Args:
            data: DataFrame with ETF returns
            regime: Specific regime to filter for, or None for all data
            min_observations: Minimum required observations
        
        Returns:
            tuple: (allocation_dict, expected_return, sharpe_ratio) or (None, None, None)
        """
        
        # Filter data by regime if specified
        if regime:
            regime_data = data[data['Regime'] == regime].copy()
        else:
            regime_data = data.copy()
        
        if len(regime_data) < min_observations:
            return None, None, None
        
        # Get ETF columns
        etf_cols = [col for col in regime_data.columns if col not in ['Date', 'Regime']]
        returns_matrix = regime_data[etf_cols].dropna()
        
        if returns_matrix.empty or len(returns_matrix) < min_observations:
            return None, None, None
        
        # Calculate statistics
        mean_returns = returns_matrix.mean()
        cov_matrix = returns_matrix.cov()
        n_assets = len(etf_cols)
        
        # Objective function: negative Sharpe ratio
        def objective(weights):
            portfolio_return = np.sum(weights * mean_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -portfolio_return / portfolio_volatility if portfolio_volatility > 0 else np.inf
        
        # Constraints and bounds
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, self.max_allocation) for _ in range(n_assets))
        x0 = np.array([1/n_assets] * n_assets)
        
        # Optimize
        try:
            result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                weights = result.x
                portfolio_return = np.sum(weights * mean_returns)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
                
                allocation = dict(zip(etf_cols, weights))
                return allocation, portfolio_return, sharpe_ratio
            
        except Exception as e:
            print(f"Optimization failed: {e}")
        
        return None, None, None
    
    def analyze_all_regimes(self):
        """Analyze optimal allocations for all regimes in both periods."""
        print("\n" + "="*60)
        print("PORTFOLIO OPTIMIZATION")
        print("="*60)
        
        regimes = [r for r in self.merged_data['Regime'].unique() if r != 'Insufficient Data']
        results = {'Pre-GARP': {}, 'Post-GARP': {}}
        
        # Analyze both periods
        for period_name, data in [('Pre-GARP', self.pre_garp_data), ('Post-GARP', self.post_garp_data)]:
            print(f"\n{period_name} PERIOD OPTIMIZATION:")
            print("-" * 40)
            
            for regime in regimes:
                allocation, ret, sharpe = self.optimize_portfolio(data, regime)
                n_obs = len(data[data['Regime'] == regime])
                
                if allocation is not None:
                    results[period_name][regime] = {
                        'allocation': allocation,
                        'expected_return': ret,
                        'sharpe_ratio': sharpe,
                        'observations': n_obs
                    }
                    
                    print(f"\n{regime}:")
                    print(f"  Observations: {n_obs}")
                    print(f"  Expected Return: {ret:.2%}")
                    print(f"  Sharpe Ratio: {sharpe:.3f}")
                    print("  Optimal Allocation:")
                    
                    # Sort by weight for better readability
                    sorted_allocation = sorted(allocation.items(), key=lambda x: x[1], reverse=True)
                    for etf, weight in sorted_allocation:
                        if weight > 0.01:  # Only show allocations > 1%
                            print(f"    {etf}: {weight:.1%}")
                else:
                    print(f"\n{regime}: Insufficient data for optimization")
        
        return results
    
    def create_summary_table(self, results):
        """Create a clean summary table of all allocations."""
        print("\n" + "="*60)
        print("ALLOCATION SUMMARY")
        print("="*60)
        
        summary_data = []
        
        for period in ['Pre-GARP', 'Post-GARP']:
            print(f"\n{period} PERIOD:")
            print("-" * 40)
            
            for regime, data in results[period].items():
                if data and 'allocation' in data:
                    allocation = data['allocation']
                    sharpe = data['sharpe_ratio']
                    
                    print(f"\n{regime} (Sharpe: {sharpe:.3f}):")
                    
                    # Sort allocations by weight
                    sorted_alloc = sorted(allocation.items(), key=lambda x: x[1], reverse=True)
                    
                    allocation_str = []
                    for etf, weight in sorted_alloc:
                        if weight > 0.01:
                            allocation_str.append(f"{etf}: {weight:.1%}")
                            summary_data.append({
                                'Period': period,
                                'Regime': regime,
                                'ETF': etf,
                                'Weight': weight,
                                'Sharpe_Ratio': sharpe
                            })
                    
                    print("  " + " | ".join(allocation_str))
        
        return pd.DataFrame(summary_data)
    
    def export_results(self, results, filename='optimal_etf_allocations_constrained.csv'):
        """Export results to CSV."""
        export_data = []
        
        for period in ['Pre-GARP', 'Post-GARP']:
            for regime, data in results[period].items():
                if data and 'allocation' in data:
                    for etf, weight in data['allocation'].items():
                        if weight > 0.001:
                            export_data.append({
                                'Period': period,
                                'Regime': regime,
                                'ETF': etf,
                                'Weight': weight,
                                'Expected_Return': data['expected_return'],
                                'Sharpe_Ratio': data['sharpe_ratio'],
                                'Observations': data['observations']
                            })
        
        df = pd.DataFrame(export_data)
        df.to_csv(filename, index=False)
        print(f"\nResults exported to: {filename}")
        return df
    
    def run_analysis(self):
        """Execute the complete analysis."""
        print("ETF REGIME-BASED ALLOCATION ANALYSIS")
        print(f"Maximum allocation per ETF: {self.max_allocation:.0%}")
        
        # Load and prepare data
        self.load_data()
        self.merge_data()
        self.split_periods()
        
        # Optimize allocations
        results = self.analyze_all_regimes()
        
        # Create summary and export
        summary_df = self.create_summary_table(results)
        export_df = self.export_results(results)
        
        print(f"\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print("Use these allocations for tactical regime-based rebalancing.")
        
        return results, summary_df, export_df


def main():
    """Main execution function."""
    # Configuration
    ETF_DATA_FILE = "consolidated_etf_performance_with_usd.csv"
    REGIME_DATA_FILE = "dates_and_regimes.csv"
    MAX_ALLOCATION_PER_ETF = 0.25  # 25% maximum
    
    # Run analysis
    optimizer = ETFRegimeOptimizer(
        etf_data_path=ETF_DATA_FILE,
        regime_data_path=REGIME_DATA_FILE,
        max_allocation=MAX_ALLOCATION_PER_ETF
    )
    
    results, summary, export_data = optimizer.run_analysis()
    
    return results, summary, export_data


if __name__ == "__main__":
    results, summary, export_data = main()