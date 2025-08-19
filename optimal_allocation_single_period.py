import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class ETFRegimeOptimizerSinglePeriod:
    """
    Single-period ETF portfolio optimizer with dynamic ETF universe.
    
    Features:
    - Uses entire dataset (2015-2025) as single period
    - Dynamic ETF universe - uses all available ETFs for each regime
    - Maximum 15% allocation per ETF (better diversification)
    - Two optimization methods:
      * Sharpe Ratio: Uses total volatility (standard deviation)
      * Sortino Ratio: Uses downside volatility only (downside deviation)
    - Optimizes for each economic regime separately
    - Handles missing ETF data gracefully with 0% allocation
    """
    
    def __init__(self, etf_data_path, regime_data_path, max_allocation=0.15, start_date='2015-02-28'):
        self.etf_data_path = etf_data_path
        self.regime_data_path = regime_data_path
        self.max_allocation = max_allocation
        self.start_date = pd.to_datetime(start_date)
        self.etf_data = None
        self.regime_data = None
        self.merged_data = None
        
        # Enhanced ETF name mapping for cleaner output
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
            'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-USD-Converted': 'Europe_Momentum_USD',
            'MSCI-USA-Quality-Factor-ETF': 'USA_Quality_Factor',
            'Edge-MSCI-Europe-Minimum-Volatility-UCITS-ETF-EUR-A': 'Europe_MinVol_EUR',
            'Edge-MSCI-World-Minimum-Volatility-UCITS-ETF-USD-Ac': 'World_MinVol_USD', 
            'MSCI-Global-Min-Vol-Factor-ETF': 'Global_MinVol',
            'MSCI-USA-Equal-Weighted-ETF': 'USA_EqualWeight',
            'Russell-2000-ETF': 'Russell_2000'
        }
        
    def load_data(self):
        """Load and preprocess ETF performance and regime data."""
        print("SINGLE-PERIOD ETF REGIME-BASED ALLOCATION ANALYSIS")
        print("Dynamic ETF Universe - Uses All Available ETFs")
        print("Maximum allocation per ETF: 15%")
        print(f"Analysis Period: {self.start_date.strftime('%Y-%m-%d')} onwards")
        print("Optimization Methods: Sharpe Ratio (total vol) + Sortino Ratio (downside vol)")
        print("=" * 80)
        print("LOADING DATA - SINGLE PERIOD ANALYSIS (SHARPE + SORTINO)")
        print("=" * 80)
        
        print("Loading ETF performance data...")
        self.etf_data = pd.read_csv(self.etf_data_path)
        
        # Clean column names
        self.etf_data.columns = self.etf_data.columns.str.strip()
        
        # Find date column
        date_col = self._find_date_column(self.etf_data)
        if date_col != 'Date':
            self.etf_data = self.etf_data.rename(columns={date_col: 'Date'})
        
        # Rename ETF columns using the mapping
        rename_dict = {old: new for old, new in self.etf_name_map.items() if old in self.etf_data.columns}
        self.etf_data = self.etf_data.rename(columns=rename_dict)
        
        # Parse dates and convert percentages
        self.etf_data['Date'] = pd.to_datetime(self.etf_data['Date'], format='%d-%m-%Y')
        self._convert_percentage_columns(self.etf_data)
        
        # Filter data to start from our analysis start date
        self.etf_data = self.etf_data[self.etf_data['Date'] >= self.start_date]
        
        # Remove EUR-denominated European Momentum ETF to avoid currency inconsistency
        # Keep only the USD-converted version
        if 'Europe_Momentum_EUR' in self.etf_data.columns:
            self.etf_data = self.etf_data.drop('Europe_Momentum_EUR', axis=1)
            print("Removed EUR-denominated European Momentum ETF (using USD-converted version only)")
        
        # Load regime data
        print("Loading economic regime data...")
        self.regime_data = pd.read_csv(self.regime_data_path)
        self.regime_data['Date'] = pd.to_datetime(self.regime_data['Date'], format='%Y-%m-%d')
        
        print(f"Loaded {len(self.etf_data)} ETF observations from {self.start_date.strftime('%d-%m-%Y')} onwards")
        print(f"Loaded {len(self.regime_data)} regime classifications")
        
    def _find_date_column(self, df):
        """Find the date column in the dataframe."""
        for col in df.columns:
            if col.lower().strip() in ['date', 'dates']:
                return col
        return df.columns[0]
    
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
        
        # Get available ETFs count
        etf_cols = [col for col in self.merged_data.columns if col not in ['Date', 'Regime']]
        print(f"Available ETFs: {len(etf_cols)}")
        
    def get_available_etfs_for_regime(self, regime_data):
        """Get ETFs that have sufficient data for a given regime."""
        etf_cols = [col for col in regime_data.columns if col not in ['Date', 'Regime']]
        available_etfs = []
        
        for etf in etf_cols:
            # Count non-null observations
            non_null_count = regime_data[etf].notna().sum()
            # Require at least 60% of observations to be non-null
            if non_null_count >= len(regime_data) * 0.6:
                available_etfs.append(etf)
        
        return available_etfs
    
    def calculate_portfolio_metrics(self, returns, weights, method='sharpe'):
        """Calculate portfolio metrics for given weights."""
        if len(returns) == 0 or returns.sum().sum() == 0:
            return 0, 0, 0
        
        # Calculate portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Calculate metrics
        mean_return = portfolio_returns.mean()
        
        if method == 'sharpe':
            # Use total volatility (standard deviation)
            volatility = portfolio_returns.std()
            if volatility == 0:
                return mean_return, 0, 0
            ratio = mean_return / volatility
        else:  # sortino
            # Use downside volatility only
            downside_returns = portfolio_returns[portfolio_returns < 0]
            if len(downside_returns) == 0:
                downside_vol = 0.001  # Small positive number to avoid division by zero
            else:
                downside_vol = downside_returns.std()
            
            if downside_vol == 0:
                return mean_return, 0, float('inf') if mean_return > 0 else 0
            ratio = mean_return / downside_vol
            
        return mean_return, volatility if method == 'sharpe' else downside_vol, ratio
    
    def optimize_regime_portfolio(self, regime_data, regime_name, method='sharpe'):
        """Optimize portfolio for a specific regime using specified method."""
        available_etfs = self.get_available_etfs_for_regime(regime_data)
        
        if len(available_etfs) == 0:
            print(f"    Warning: No ETFs available for regime {regime_name}")
            return None, None, None, None
        
        # Get returns for available ETFs only, drop NaN rows
        returns_data = regime_data[available_etfs].dropna()
        
        if len(returns_data) == 0:
            print(f"    Warning: No valid data for regime {regime_name}")
            return None, None, None, None
        
        n_assets = len(available_etfs)
        
        # Objective function to maximize ratio (minimize negative ratio)
        def objective(weights):
            _, _, ratio = self.calculate_portfolio_metrics(returns_data, weights, method)
            return -ratio  # Minimize negative ratio = maximize ratio
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # Weights sum to 1
        ]
        
        # Bounds - each weight between 0 and max_allocation
        bounds = [(0, self.max_allocation) for _ in range(n_assets)]
        
        # Initial guess - equal weights up to max_allocation
        initial_weight = min(1.0 / n_assets, self.max_allocation)
        x0 = np.full(n_assets, initial_weight)
        x0 = x0 / np.sum(x0)  # Normalize
        
        # Optimize
        try:
            result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                optimal_weights = result.x
                mean_return, vol, ratio = self.calculate_portfolio_metrics(returns_data, optimal_weights, method)
                
                # Create allocation dictionary with all ETFs (0% for unavailable ones)
                all_etf_cols = [col for col in self.merged_data.columns if col not in ['Date', 'Regime']]
                allocations = {}
                for i, etf in enumerate(available_etfs):
                    if optimal_weights[i] >= 0.001:  # Only show meaningful allocations
                        allocations[etf] = optimal_weights[i]
                
                return allocations, mean_return, ratio, len(returns_data)
            else:
                print(f"    Optimization failed for {regime_name}: {result.message}")
                return None, None, None, None
                
        except Exception as e:
            print(f"    Error optimizing {regime_name}: {str(e)}")
            return None, None, None, None
    
    def analyze_regimes(self):
        """Analyze all regimes using both optimization methods."""
        print("\n" + "=" * 80)
        print("SINGLE-PERIOD PORTFOLIO OPTIMIZATION (SHARPE + SORTINO)")
        print("=" * 80)
        
        results = {
            'Single Period (2015-2025)': {'sharpe': {}, 'sortino': {}}
        }
        
        regimes = self.merged_data['Regime'].unique()
        
        print(f"\nSingle Period ({self.merged_data['Date'].min().strftime('%Y-%m-%d')} to {self.merged_data['Date'].max().strftime('%Y-%m-%d')}):")
        print("-" * 60)
        
        for method in ['sharpe', 'sortino']:
            method_name = method.upper()
            print(f"\n  {method_name} RATIO OPTIMIZATION:")
            print("  " + "-" * 40)
            
            for regime in sorted(regimes):
                regime_data = self.merged_data[self.merged_data['Regime'] == regime].copy()
                
                if len(regime_data) < 5:  # Skip regimes with too few observations
                    print(f"\n    {regime}:")
                    print(f"      Skipped: Only {len(regime_data)} observations")
                    continue
                
                allocations, expected_return, ratio, observations = self.optimize_regime_portfolio(
                    regime_data, regime, method
                )
                
                if allocations is not None:
                    # Store results
                    results['Single Period (2015-2025)'][method][regime] = {
                        'allocations': allocations,
                        'expected_return': expected_return * 100,  # Convert to percentage
                        'ratio': ratio,
                        'observations': observations
                    }
                    
                    print(f"\n    {regime}:")
                    print(f"      Observations: {observations}")
                    print(f"      Expected Return: {expected_return * 100:.2f}%")
                    print(f"      {method_name} Ratio: {ratio:.3f}")
                    print(f"      Optimal Allocation:")
                    
                    # Sort allocations by weight for better readability
                    sorted_allocations = sorted(allocations.items(), key=lambda x: x[1], reverse=True)
                    for etf, weight in sorted_allocations:
                        print(f"        {etf}: {weight*100:.1f}%")
        
        return results
    
    def export_results(self, results, filename='optimal_etf_allocations_single_period.csv'):
        """Export results to CSV file."""
        rows = []
        
        for period, methods in results.items():
            for method, regimes in methods.items():
                for regime, data in regimes.items():
                    for etf, weight in data['allocations'].items():
                        rows.append({
                            'Period': period,
                            'Method': method.title(),
                            'Regime': regime,
                            'ETF': etf,
                            'Weight': weight,
                            'Expected_Return': data['expected_return'] / 100,  # Convert back to decimal
                            'Ratio_Value': data['ratio'],
                            'Observations': data['observations']
                        })
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f"\nResults exported to: {filename}")
        
        return df
    
    def run_analysis(self):
        """Run the complete analysis pipeline."""
        self.load_data()
        self.merge_data()
        results = self.analyze_regimes()
        df = self.export_results(results)
        
        print("\n" + "=" * 80)
        print("SINGLE-PERIOD ANALYSIS COMPLETE!")
        print("=" * 80)
        print("Key features:")
        print("• Single time period (2015-2025) with maximum data usage")
        print("• Dynamic ETF universe - uses all available ETFs per regime")
        print("• Sharpe ratio optimization (penalizes all volatility)")
        print("• Sortino ratio optimization (penalizes only downside volatility)")
        print("• Currency-consistent USD allocations")
        print("• Professional 15% maximum allocation constraint")
        
        return results, df


def main():
    """
    Main function to run single-period ETF regime-based optimization
    """
    optimizer = ETFRegimeOptimizerSinglePeriod(
        etf_data_path='consolidated_etf_performance_with_usd.csv',
        regime_data_path='economic_regimes_classified.csv',
        max_allocation=0.15
    )
    
    results, df = optimizer.run_analysis()
    return results, df


if __name__ == "__main__":
    main()